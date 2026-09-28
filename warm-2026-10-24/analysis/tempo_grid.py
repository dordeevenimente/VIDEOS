import librosa, numpy as np
y, sr = librosa.load('track.wav', sr=44100, mono=True)
hop=64
o=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop,fmax=150,n_mels=32)
tt=np.arange(len(o))*hop/sr
m=(tt>6.5)&(tt<81)
best=None
for bpm in np.arange(126.5,127.51,0.05):
    b=60/bpm
    for ph in np.arange(0,b,0.002):
        g=ph+np.arange(0,82/b)*b; g=g[(g>6.5)&(g<81)]
        s=o[np.clip((g*sr/hop).astype(int),0,len(o)-1)].sum()
        if best is None or s>best[0]: best=(s,bpm,ph)
s,bpm,ph=best; b=60/bpm
first=ph+b*np.ceil((6.6-ph)/b)
print('BPM %.2f beat %.4f s  grid phase %.3f  first groove beat %.3f'%(bpm,b,ph,first))
print('bar %.4f s, 8-bar phrase %.3f s'%(4*b,32*b))
for k in range(0,12): print('phrase',k, round(first-32*b+ k*8*4*b,3), ' 4-bar:', [round(first+ (k*8+j)*4*b -32*b,2) for j in (0,4)])
