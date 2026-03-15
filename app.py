import streamlit as st
import streamlit.components.v1 as components
import requests
import os
from dotenv import load_dotenv
from groq import Groq

# ---------------- Load API Keys ----------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# ---------------- Page Setup ----------------
st.set_page_config(page_title="AI Voice Assistant", layout="wide")

# ---------------- Fixed Footer Style ----------------
st.markdown("""
<style>

.footer {
position: fixed;
bottom: 0;
left: 0;
width: 100%;
background: #0f172a;
color: #cbd5f5;
text-align: center;
padding: 12px;
font-size: 14px;
border-top: 1px solid rgba(255,255,255,0.1);
z-index: 999;
}

.footer a{
color:#38bdf8;
text-decoration:none;
margin:0 10px;
}

.footer a:hover{
text-decoration:underline;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Animated Voice UI ----------------
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
body, html {
margin:0;
padding:0;
width:100%;
height:100%;
background-color:#050a14;
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
font-family:'Segoe UI',sans-serif;
overflow:hidden;
}

h1{
color:white;
font-weight:300;
font-size:2.5rem;
margin-bottom:50px;
letter-spacing:1px;
opacity:0.9;
}

canvas{
position:absolute;
bottom:20%;
left:0;
width:100%;
height:200px;
}
</style>
</head>

<body>

<h1>What can I help you with?</h1>

<canvas id="waveCanvas"></canvas>

<script>

const canvas = document.getElementById('waveCanvas');
const ctx = canvas.getContext('2d');

let width,height,amplitude,frequency,speed;
let step = 0;

function resize(){
width = canvas.width = window.innerWidth;
height = canvas.height = 200;
amplitude = 40;
frequency = 0.01;
speed = 0.05;
}

window.addEventListener('resize',resize);
resize();

function drawWave(color,opacity,offset,speedModifier){
ctx.beginPath();
ctx.lineWidth = 2;
ctx.strokeStyle = color;
ctx.globalAlpha = opacity;

for(let x=0;x<width;x++){

const y = height/2 +
Math.sin(x*frequency + step*speedModifier + offset)
* amplitude * Math.sin(step*0.02);

if(x===0){ctx.moveTo(x,y);}
else{ctx.lineTo(x,y);}

}

ctx.stroke();
}

function animate(){
ctx.clearRect(0,0,width,height);

drawWave('#4fc3f7',0.8,0,1);
drawWave('#2196f3',0.5,2,0.8);
drawWave('#00e5ff',0.3,4,1.2);

step += speed;
requestAnimationFrame(animate);
}

animate();

</script>

</body>
</html>
""", height=350)

# ---------------- Input Form ----------------
with st.form("question_form"):
    question = st.text_input("Ask your AI assistant...")
    submitted = st.form_submit_button("Ask AI")

# ---------------- AI + Voice ----------------
if submitted and question:

    with st.spinner("Thinking..."):

        chat = client.chat.completions.create(
            messages=[{"role":"user","content":question}],
            model="llama-3.1-8b-instant"
        )

        answer = chat.choices[0].message.content[:3000]

    st.write("### 🤖 AI Response")
    st.write(answer)

    # ---------------- Murf Voice Generation ----------------

    url = "https://api.murf.ai/v1/speech/generate"

    payload = {
        "text": answer,
        "voiceId": "en-US-natalie",
        "format": "mp3"
    }

    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }

    audio_url = None

    status = st.status("🔊 Generating AI voice...", expanded=False)

    for attempt in range(3):

        try:
            res = requests.post(url,json=payload,headers=headers)

            if res.status_code == 200:
                audio_url = res.json()["audioFile"]
                break

        except:
            pass

    if audio_url:

        status.update(label="✅ Voice generated successfully", state="complete")
        st.audio(audio_url)

    else:

        status.update(label="⚠ Voice generation failed", state="error")

# ---------------- Footer ----------------
st.markdown("""
<div class="footer">
Built by <b>Harsha D</b> | B.Tech Student |
<a href="https://github.com/harshadev1428" target="_blank">GitHub</a>
<a href="https://linkedin.com/in/harsha-d-9aba27372" target="_blank">LinkedIn</a>
<a href="mailto:hharshadev2006@gmail.com">Email</a>
<br>
© 2026 AI Voice Assistance
</div>
""", unsafe_allow_html=True)