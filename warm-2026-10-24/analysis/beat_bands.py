import librosa, numpy as np
y, sr = librosa.load('track.wav', sr=44100, mono=True)
S_=np.abs(librosa.stft(y,n_fft=2048,hop_length=256)); f=librosa.fft_frequencies(sr=sr); t=librosa.frames_to_time(np.arange(S_.shape[1]),sr=sr,hop_length=256)
def band(a,b): return 20*np.log10(S_[(f>=a)&(f<b)].mean(0)+1e-9)
B={'sub':band(30,90),'lmid':band(150,400),'mid':band(400,2500),'pres':band(2500,6000),'air':band(8000,16000)}
beat=60/127; g0=7.062
def row(a,w):
    m=(t>=a)&(t<a+w); return '  '.join(f"{v[m].mean():6.1f}" for v in B.values())
print('--- per beat, intro and phrase 1-2 ---')
for k in range(-15,40):
    a=g0+k*beat; bar=k//4; 
    if a<0: continue
    print(f"b{k:4d} bar{bar:3d}.{k%4+1} {a:6.2f} {row(a,beat)}")
print('--- per beat 76-90 ---')
for k in range(146,176):
    a=g0+k*beat; print(f"b{k:4d} bar{k//4:3d}.{k%4+1} {a:6.2f} {row(a,beat)}")
