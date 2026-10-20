export GRADY=0.69
j(){ OVSET= python3 render_reel.py $1 $2 story > /dev/null 2>&1 && echo "done $2" || echo "FAIL $2"; }
s(){ OVSET=ovSV python3 render_reel.py $1 $2 story > /dev/null 2>&1 && echo "done $2" || echo "FAIL $2"; }
j src2.mp4 WARM_JUST2_reel_A_STORY_1080x1920.mp4 & j src1.mp4 WARM_JUST2_reel_B_STORY_1080x1920.mp4 & j src3.mp4 WARM_JUST2_reel_C_STORY_1080x1920.mp4 & wait
j src4.mp4 WARM_JUST2_reel_D_STORY_1080x1920.mp4 & j src5.mp4 WARM_JUST2_reel_E_STORY_1080x1920.mp4 & j src7.mp4 WARM_JUST2_reel_G_STORY_1080x1920.mp4 & wait
j src8.mp4 WARM_JUST2_reel_H_STORY_1080x1920.mp4 & s salvi/src_s1.mp4 salvi/WARM_SALVI_reel_1_STORY_1080x1920.mp4 & s salvi/src_s2.mp4 salvi/WARM_SALVI_reel_2_STORY_1080x1920.mp4 & wait
echo ALL_DONE
