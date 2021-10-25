import obspython as obs

TSourceOutputName = "" # Text source being written to in OBS
indexFile = "" # List of input text files to fuze
formattingString = "" # Formatting string for the output text
refreshTime = 5 # Refresh time of the text source

# ACTUAL TEXT UPDATING ------------------------------------------------------------

def update_text(props, prop):
    global TSourceOutputName
    global indexFile
    global formattingString

    # Read every line of the file at indexFile and add it to an array
    paths = []

    with open(indexFile) as file:
        a = file.readlines()
        for line in a:
            paths.append(line.strip())
             
    # Add the text of every file in paths to an array called texts
    texts = []
    for path in paths:
        with open(path) as file:
            texts.append(file.read())

    output_text = formattingString
    # Format the output text
    for i in range(len(texts)):
        if "%" + str(i+1) in output_text:
            output_text = output_text.replace("%" + str(i+1), texts[i])

    # Update the text source
    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "text", output_text)
    obs.obs_source_update(obs.obs_get_source_by_name(TSourceOutputName), settings)
    obs.obs_data_release(settings) # #NoMemLeaks

# OBS SETTINGS STUFF------------------------------------------------------------

def script_description():
    return "Fuze text files and inject the output into a text source.\nThe Index file directory should be a list of file directorys for the text files you want to merge. Each file on its own line.\nUse `%I` where I is the number of the file you gave in (1 indexed) in the formating string to define how you want the outputed text to look. EX: `%1 - %2 / Song by: %3` \n\nBy SuperZooper3"

def script_update(settings):
    global TSourceOutputName
    global indexFile
    global refreshTime
    global formattingString

    TSourceOutputName = obs.obs_data_get_string(settings, "TSourceOutputName")
    indexFile = obs.obs_data_get_string(settings, "indexFile")
    formattingString = obs.obs_data_get_string(settings, "formattingString")
    refreshTime = obs.obs_data_get_int(settings, "refreshTime") 

    # Update the refresh timer
    obs.timer_remove(refresh_text)
    
    if refreshTime > 0 and TSourceOutputName != "" and indexFile != "" and formattingString != "":
        obs.timer_add(refresh_text, refreshTime * 1000)

def script_defaults(settings): # Sets the defaults for the values in the obs editor
    obs.obs_data_set_default_int(settings, "refreshTime", 5)

# This needs to be here for the refresh button to work
def refresh_text():
    update_text(props="", prop="")

def script_properties(): # Get the property boxes so we cant use them here
    props = obs.obs_properties_create()

    # All of the input boxes

    # The text source 
    p = obs.obs_properties_add_list(props, "TSourceOutputName", "Text Output Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
          
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)
        obs.source_list_release(sources)

    obs.obs_properties_add_path(props, "indexFile", "Index File Directory", obs.OBS_PATH_FILE, "", "")
    obs.obs_properties_add_text(props, "formattingString", "Formatting String", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "refreshTime", "Refresh Time", 1, 600, 1)
    
    # Refresh button 
    obs.obs_properties_add_button(props, "button", "Refresh", update_text)

    return props
