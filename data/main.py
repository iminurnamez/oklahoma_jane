from . import tools, prepare
from .states import junglegame, controlsscreen


def main():
    run_it = tools.Control(prepare.ORIGINAL_CAPTION)
    state_dict = {"GAME": junglegame.Game(),
                        "CONTROLSSCREEN": controlsscreen.ControlsScreen()}
                        
    run_it.setup_states(state_dict, "GAME")
    run_it.main()
