import numpy as np
import pandas as pd
from pathlib import Path

from stytra import Stytra
from stytra.stimulation import Protocol
from stytra.stimulation.stimuli import InterpolatedStimulus, CalibratedCircleStimulus
from stytra.stimulation.stimuli.visual import Pause

from stytra.stimulation.estimators import SimulatedPositionEstimator

from lightparam import Param

class DotStimulus(InterpolatedStimulus, CalibratedCircleStimulus):
    name = "dot_stimulus"

class DotProtocol(Protocol):
    name = "dot_protocol"  
    stytra_config = dict(
        tracking=dict(
            method="fish",
            embedded = False,
            estimator = SimulatedPositionEstimator,
            estimator_params=dict(
                motion=pd.DataFrame(
                    dict(
                        t=[0,5,120],
                        x=[100,100,100],
                        y=[10,10,10],
                        theta=[0,0, np.pi/2]
                    )
                )
            ),
        ),
        camera=dict(
            video_file=str(
                Path(__file__).parent / "assets" / "fish_free_compressed.h5"
            ),
            min_framerate=100,
        ),
    )

    def __init__(self):
        super().__init__()
    
        self.n_movements = Param(10, limits=(0, 1000))

        self.x_pos_pix = Param(10, limits=(0, 100))
        self.y_pos_pix = Param(10, limits=(0, 100))
        self.movement_x = Param(10, limits=(0,40))
        self.movement_y = Param(10, limits=(0,40))

        self.raidus = Param(2.0, limits=(0,100))
        self.start_t = Param(1.0, limits=(0.0,100.0))
        self.end_t = Param(1.5, limits=(0.0,100.0))

        self.pause_length = Param (1.0, limits=(0.0, 10.0))

    def get_stim_sequence(self):
        stimuli = []

        x_start = self.x_pos_pix
        y_start = self.y_pos_pix
        x_final = 0
        y_final = 0

        n_operations = 0

        for i in range(self.n_movements):

            x_move = np.random.rand() * self.movement_x
            y_move = np.random.rand() * self.movement_y

            if (i % 2 == 0):                
                if (x_start + x_move > 40 and x_start-x_move < 0):
                    x_final = np.randint(10)
                elif (x_start + x_move > 40 and x_start-x_move > 0):
                    x_final = x_start - x_move
                else:
                    x_final = x_start + x_move 

                if (y_start + y_move > 40 and y_start-y_move < 0):
                    y_final = np.randint(10)
                elif (y_start + y_move > 40 and y_start-y_move > 0):
                    y_final = y_start - y_move
                else:
                    y_final = y_start + y_move 

                origin_df = pd.DataFrame(
                    dict(
                        t=[1.0, 1.5],
                        #t=[self.start_t, self.end_t],
                        x=[x_start, x_final],
                        y=[y_start, y_final], 
                    )
                )

                x_start = x_final
                y_start = y_final
                
            else:
                origin_df = pd.DataFrame(
                    dict(
                    t=[0, 0.5],
                    x=[x_start, x_start],
                    y=[y_start, y_final]
                    )
                )

            stimuli.append(
                DotStimulus(
                    background_color=(255, 255, 255),
                    circle_color=(0, 0, 0),
                    radius=self.raidus,
                    df_param=origin_df
                )       
            )
            #stimuli.append(
            #    Pause(duration = self.pause_length)
            #)
        return stimuli

'''
Still need to do
- Implement a "pause" function (since zebrafish stop and then move again)
    - Using Pause(duration = __) doesn't work since it makes the screen fully black
- Implement tracking
- More aggressive movements
- Determine the overall window size
'''

if __name__ == "__main__":
    s = Stytra(protocol = DotProtocol())