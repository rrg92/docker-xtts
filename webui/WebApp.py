import gradio as gr
import requests
import base64
import tempfile
import json
import os
from os.path import abspath
import zipfile
import random

SERVER_URL = os.getenv('XTTS_SERVER', 'http://localhost:8000') 
DO_CHECK = os.getenv('DO_CHECK', '1') 

OUTPUT = "./demo_outputs"
cloned_speakers = {}

print("Preparing file structure...")
if not os.path.exists(OUTPUT):
    os.mkdir(OUTPUT)
    os.mkdir(os.path.join(OUTPUT, "cloned_speakers"))
    os.mkdir(os.path.join(OUTPUT, "generated_audios"))
elif os.path.exists(os.path.join(OUTPUT, "cloned_speakers")):
    print("Loading existing cloned speakers...")
    for file in os.listdir(os.path.join(OUTPUT, "cloned_speakers")):
        if file.endswith(".json"):
            with open(os.path.join(OUTPUT, "cloned_speakers", file), "r") as fp:
                cloned_speakers[file[:-5]] = json.load(fp)
    print("Available cloned speakers:", ", ".join(cloned_speakers.keys()))

AUDIOS_DIR = os.path.join("demo_outputs", "generated_audios");
ZIP_DIR = os.path.join("zip_outputs");

print("Checking zip at", ZIP_DIR)
if not os.path.exists(ZIP_DIR):
    os.mkdir(ZIP_DIR)


try:
    print("Getting metadata from server ...")
    LANUGAGES = requests.get(SERVER_URL + "/languages").json()
    print("Available languages:", ", ".join(LANUGAGES))
    STUDIO_SPEAKERS = requests.get(SERVER_URL + "/studio_speakers").json()
    print("Available studio speakers:", ", ".join(STUDIO_SPEAKERS.keys()))
except:
    raise Exception("Please make sure the server is running first.")


def ExtractVars(input_string):
    # Split the string into lines
    lines = input_string.split('\n')
    
    # Initialize an empty dictionary to store key-value pairs
    result_dict = {
         'prefix': None,
         'name': '',
         'speaker': None,
         'num': None,
    }
    
    # List to hold lines that do not start with '!'
    filtered_lines = []
    
    # Iterate through each line
    for line in lines:
        # Check if the line starts with '!'
        if line.strip().startswith('!'):
            
            # Try to split the line into key and value parts
            try:
                # Split on '=' and strip whitespace from key and value
                key, value = line.strip()[1:].split('=')
                key = key.strip()
                value = value.strip()
                # Add to dictionary
                result_dict[key] = value
            except ValueError:
                # Handle the case where there is no '=' or improper format
                continue
        elif len(line.strip()) > 0:
            # Add the line to filtered_lines if it doesn't start with '!'
            filtered_lines.append(line)
    
    # Join the filtered lines back into a single string
    filtered_string = '\n'.join(filtered_lines)
    return result_dict, filtered_string


def FindSpeakerByName(name, speakerType):

    srcItems = STUDIO_SPEAKERS if speakerType == "Studio" else cloned_speakers;
    
    for key, value in srcItems.items():
        
        if key == name:
            return key,value 
            
        if key.split(" ")[0] == name:
            return key,value;
            
            
def clone_speaker(upload_file, clone_speaker_name, cloned_speaker_names):
    files = {"wav_file": ("reference.wav", open(upload_file, "rb"))}
    embeddings = requests.post(SERVER_URL + "/clone_speaker", files=files).json()
    with open(os.path.join(OUTPUT, "cloned_speakers", clone_speaker_name + ".json"), "w") as fp:
        json.dump(embeddings, fp)
    cloned_speakers[clone_speaker_name] = embeddings
    cloned_speaker_names.append(clone_speaker_name)
    return upload_file, clone_speaker_name, cloned_speaker_names, gr.Dropdown.update(choices=cloned_speaker_names)

def tts(text, speaker_type, speaker_name_studio, speaker_name_custom, lang, temperature
    ,speed,top_p,top_k, AllFileList,progress=gr.Progress()
):
    embeddings = STUDIO_SPEAKERS[speaker_name_studio] if speaker_type == 'Studio' else cloned_speakers[speaker_name_custom]
    
    # break at line!
    lines = text.split("---");
    totalLines = len(lines);
    print("Total parts:", len(lines))
    
    audioNum = 0;
    
    DefaultPrefix = next(tempfile._get_candidate_names());
    
    CurrentPrefix = DefaultPrefix
    
    
    AudioList = [];
    for line in progress.tqdm(lines, desc="Gerando fala..."):
        audioNum += 1;
         
        textVars,cleanLine = ExtractVars(line)

        if textVars['prefix']:
            CurrentPrefix = textVars['prefix']

        audioName = textVars['name'];
        
        if audioName:
            audioName = '_'+audioName

        num = textVars['num'];
        
        if not num:
            num = audioNum;
        
        path = CurrentPrefix +"_n_" + str(num)+audioName+".wav"

        print("Generating audio for line", num, 'sequence', audioNum);
        
        speaker = textVars['speaker'];
        
        if not speaker:
            speaker = speaker_name_studio if speaker_type == 'Studio' else speaker_name_custom
        
        speakerName,embeddings = FindSpeakerByName(speaker, speaker_type)
        
        if not speakerName:
             raise ValueError("InvalidSpeaker: "+speakerName) 

        generated_audio = requests.post(
            SERVER_URL + "/tts",
            json={
                "text": cleanLine,
                "language": lang,
                "speaker_embedding": embeddings["speaker_embedding"],
                "gpt_cond_latent": embeddings["gpt_cond_latent"],
                "temperature": temperature,
                "speed": speed,
                "top_p": top_p,
                "top_k": top_k,
            }
        ).content
    
        print("Audio generated.. Saving to", path);
        generated_audio_path = os.path.join(AUDIOS_DIR, path)
        with open(generated_audio_path, "wb") as fp:
            fp.write(base64.b64decode(generated_audio))
            AudioList.append(fp.name);
    
    AllFileList.clear();
    AllFileList.extend(AudioList);
    
    return gr.Dropdown(
            label="Generated Audios",
            choices=list(AudioList),
            value=AudioList[0]
        )
            
def get_file_content(f):
    if len(f) > 0:
        return f[0];
        
    return None;


def UpdateFileList(DirListState):
    DirListState.clear();
    DirListState.extend( os.listdir(AUDIOS_DIR) )
     
def audio_list_update(d):
    fullPath = abspath(d)
    return fullPath
    
def ZipAndDownload(files):
    allFiles = files
    
    DefaultPrefix = next(tempfile._get_candidate_names());
    
    zipFile = abspath( os.path.join(ZIP_DIR, DefaultPrefix + ".zip") );
    
    
    with zipfile.ZipFile(zipFile, 'w') as zipMe:        
        for file in allFiles:
            print("Zipping", file);
            zipMe.write(abspath(file), os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)
    
    print("Pronto",  zipFile);
    
    return '<a href="/file='+zipFile+'">If donwload dont starts, click here</a>';
   

js = """
function DetectDownloadLink(){
    console.log('Configuring AutoDonwloadObservr...');
    let hiddenLink = document.getElementById("DonwloadLink");
    let onChange= function(mutations){
        
         for (const mutation of mutations) {
            if (mutation.type !== 'childList')
                continue;

              for (const addedNode of mutation.addedNodes) {
                if (addedNode.nodeName === 'A') {
                    location.href = addedNode.href;
                }
              }

          }
    }
    
    let config = {  attributes: true, childList: true, subtree: true, attributeFilter: ["href"] }
    let obs = new MutationObserver(onChange);
    obs.observe(hiddenLink, config);
}
"""

with gr.Blocks(js=js) as demo:
    defaultSpeaker = "Dionisio Schuyler"
    cloned_speaker_names = gr.State(list(cloned_speakers.keys()))
    AllFileList = gr.State(list([]))

    
    with gr.Tab("TTS"):
        with gr.Column() as row4:
            with gr.Row() as col4:
                speaker_name_studio = gr.Dropdown(
                    label="Studio speaker",
                    choices=STUDIO_SPEAKERS.keys(),
                    value=defaultSpeaker if defaultSpeaker in STUDIO_SPEAKERS.keys() else None,
                )
                speaker_name_custom = gr.Dropdown(
                    label="Cloned speaker",
                    choices=cloned_speaker_names.value,
                    value=cloned_speaker_names.value[0] if len(cloned_speaker_names.value) != 0 else None,
                )
            speaker_type = gr.Dropdown(label="Speaker type", choices=["Studio", "Cloned"], value="Studio")
        with gr.Column() as rowAdvanced:
             with gr.Row() as rowAdvanced:
                temperature = gr.Slider(0.00, 1.00, 0.5, step=0.05, label="Temperature", info="Choose between 0 and 1")
                top_p = gr.Slider(0.00, 1.00, 0.8, step=0.05, label="TOP P", info="Choose between 0 and 1")
                top_k = gr.Number(label="TOP K",value=50)
                speed = gr.Slider(0.00, 1000.00, 1.0, step=0.1, label="Speed", info="Speed (0 to 1000)")
        with gr.Column() as col2:
            lang = gr.Dropdown(label="Language", choices=LANUGAGES, value="pt")
            text = gr.Textbox(label="text",lines=4, value="A quick brown fox jumps over the lazy dog.")
            tts_button = gr.Button(value="TTS")   
        with gr.Column() as col3:
            # FileList = gr.FileExplorer(
            #     glob="*.wav",
            #     # value=["themes/utils"],
            #     ignore_glob="**/__init__.py",
            #     root_dir=AUDIOS_DIR,
            #     interactive = True,
            #     value=DirectoryList.value
            # )
            
            AudioList = gr.Dropdown(
                    label="Generated Audios",
                    choices=['a','b']
                    ,interactive=True
                )
            
            generated_audio = gr.Audio(label="Audio Play", autoplay=True)
            AudioList.change(fn=audio_list_update, inputs=[AudioList], outputs=[generated_audio])
            
            dummyHtml = gr.HTML(elem_id = "DonwloadLink", render = False); 
            downloadAll = gr.DownloadButton("Download All Files")
            downloadAll.click(ZipAndDownload, inputs=[AllFileList], outputs=[dummyHtml]);
            dummyHtml.render();
            
            
    with gr.Tab("Clone a new speaker"):
        with gr.Column() as col1:
            upload_file = gr.Audio(label="Upload reference audio", type="filepath")
            clone_speaker_name = gr.Textbox(label="Speaker name", value="default_speaker")
            clone_button = gr.Button(value="Clone speaker")

    clone_button.click(
        fn=clone_speaker,
        inputs=[upload_file, clone_speaker_name, cloned_speaker_names],
        outputs=[upload_file, clone_speaker_name, cloned_speaker_names, speaker_name_custom],
    )

    tts_button.click(
        fn=tts,
        inputs=[text, speaker_type, speaker_name_studio, speaker_name_custom, lang, temperature
                ,speed,top_p,top_k,AllFileList
                ],
        outputs=[AudioList],
    )
    
if __name__ == "__main__" and DO_CHECK == "1":
    print("Warming up server... Checking server healthy...")
    
    speakerName, embs = random.choice(list(STUDIO_SPEAKERS.items()));
   
    print("Testing with", speakerName);
    

    resp = requests.post(
        SERVER_URL + "/tts",
        json={
            "text": "This is a warmup request.",
            "language": "en",
            "speaker_embedding": embs["speaker_embedding"],
            "gpt_cond_latent": embs["gpt_cond_latent"],
            "temperature": 0.5,
            "speed": 1.0,
            "top_p": 0.8,
            "top_k": 50,
        }
    )
    
    resp.raise_for_status()
    print(" TEST OK")   


if __name__ == "__main__":
    print("STARTING...")
    demo.launch(
        share=False,
        debug=False,
        server_port=80,
        server_name="0.0.0.0",
        allowed_paths=[ZIP_DIR]
    )
