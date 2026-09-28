"""Shared timing for the WARM 24.10.26 promo — everything derives from the 127 BPM grid."""

BPM = 127.0
BEAT = 60.0 / BPM            # 0.4724 s
BAR = 4 * BEAT               # 1.8898 s
FIRST_KICK = 7.062           # first groove kick in the supplied WAV (s)

AUDIO_IN = FIRST_KICK - 3 * BAR   # 1.3927 s — intro downbeat, 3 bars before the drop
BARS = 12
FPS = 30
W, H = 1080, 1920
FRAMES = round(BARS * BAR * FPS)  # 680
DURATION = FRAMES / FPS


def bar(n, beat=0):
    """Video time of bar n (0-based), optional beat offset."""
    return n * BAR + beat * BEAT


INTRO = bar(0)
BUILD = bar(2)            # riser/fill bar
SUCK = bar(2, 2)          # highs drop out, sub swells
DROP = bar(3)             # first kick
NAME2 = bar(4)
NAME3 = bar(5)
RIFF1 = bar(6)            # mid-range stab
INFO1 = bar(7)
INFO2 = bar(8)
INFO3 = bar(9)
RIFF2 = bar(10)           # stab -> end card
LAYER = bar(11)           # new layer enters (phrase 2)
END = DURATION

# Background shots: (start, end, source, source in-point s, horizontal crop 0..1)
# "just2" = the artist's own footage (720x900, supplied); numeric ids = Adobe Stock (free).
SHOTS = [
    (INTRO, BUILD, "799935911", 4.0, 0.5),   # dark room: WARM PRESENTA
    (BUILD, DROP, "518355395", 2.0, 0.5),    # beams, riser
    (DROP, NAME2, "just2", 1.10, 0.0),       # JUST2 at the booth, his name lit behind him
    (NAME2, NAME3, "just2", 4.40, 1.0),      # second front-view take
    (NAME3, RIFF1, "just2", 15.75, 0.5),     # full room in haze: support acts
    (RIFF1, INFO1, "just2", 17.95, 0.5),     # lasers over the crowd
    (INFO1, INFO3, "757067874", 1.0, 0.5),   # hands on the mixer: date, time
    (INFO3, RIFF2, "517066238", 5.0, 0.5),   # crowd, hands up: AGUADULCE
    (RIFF2, END, "518355395", 12.0, 0.5),    # clean beams under the poster
]
