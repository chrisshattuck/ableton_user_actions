# Import UserActionsBase to extend it.
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
import time
import pprint


# Your class must extend UserActionsBase.
class ExampleActions(UserActionsBase):

    def create_actions(self):
        self.add_global_action('crossfade_random', self.crossfade_random)
        self.ambient = 1

    def prepare_args(self, args):
        args = args.split(",")
        new_args = {}
        for k, v in enumerate(args):
            arg_parts = v.split('=')
            new_args[arg_parts[0]] = arg_parts[1].strip('"\'')
        return new_args

    def log(self, message):
        self.canonical_parent.log_message(message)

    def crossfade_random(self, action_def, args):
        self.ambient = self.ambient or 1

        args = self.prepare_args(args)

        first = args['left']
        second = args['right']
        track_name = "Ambient 1"
        newoutput = ''
        tracklist = list(self.song().tracks)  # Note making a list, won't work otherwise

        try:
            for track in tracklist:
                newoutput += ('Track: %s\n' % track.name)
                self.log(track.name)
                if track.name == track_name:
                    newoutput += "THIS IS THE ONE\n"
                    t = track
                    playing_clip_slot = t.clip_slots[t.playing_slot_index]
                    newoutput += ("PLAYING CLIP:" + playing_clip_slot.clip.name + "\n")

        except Exception as e:
            self.log('\n\nERROR:\n')
            self.log(e)

        self.log("\n\nOutput:" + newoutput + '\n-----\n')


        if self.ambient == 1:
            action = '"' + first + '"/PLAY RNDC;WAIT 1;"' + first + '"/CLIP START RND song.view.detail_clip.loop_start-song.view.detail_clip.loop_end; WAIT 5; "' + second + '"/VOL RAMP 100 0; "' + first + '"/VOL RAMP 100 100;'
            #action = '"' + args[0] + '"/PLAY RNDC'
            self.ambient = 2
        else:
            action = '"' + second + '"/PLAY RNDC; WAIT 1;"' + second + '"/CLIP START RND song.view.detail_clip.loop_start-song.view.detail_clip.loop_end; WAIT 5; "' + second + '"/VOL RAMP 100 100; "' + first + '"/VOL RAMP 100 0;'
            self.ambient = 1

        self.canonical_parent.clyphx_pro_component.trigger_action_list(action)
        #self.canonical_parent.show_message('Crossfade initiated' + first + " and " + second)
        #self.canonical_parent.log_message(args[0].strip('"\''))

