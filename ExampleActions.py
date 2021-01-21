# Import UserActionsBase to extend it.
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
import time
import pprint


# Your class must extend UserActionsBase.
class ExampleActions(UserActionsBase):

    def create_actions(self):
        self.add_global_action('crossfade_random', self.crossfade_random)
        self.cf_vars = {}

    def prepare_args(self, args):
        args = args.split(",")
        new_args = {}
        for k, v in enumerate(args):
            arg_parts = v.split('=')
            new_args[arg_parts[0]] = arg_parts[1].strip('"\'')
        return new_args

    def log(self, message):
        self.canonical_parent.log_message('\n' + message + '\n')

    def crossfade_random(self, action_def, args):
        self.log('TRIGGERING')
        args = self.prepare_args(args)
        cf_id = args['left'] + args['right']

        # Initialize crossfade
        if not cf_id in self.cf_vars:
            self.cf_vars[cf_id] = args
            # Set volumes to 0
            self.cf_vars[cf_id]['playing_track_name'] = args['left']

        #self.cf_vars[cf_id] = self.cf_vars[cf_id] or {}

        newoutput = ''
        tracklist = list(self.song().tracks)  # Note making a list, won't work otherwise

        crossfade_id = args['left'] + args['right']

        try:

            #self.log("CF VARS:")
            #self.log(self.cf_vars)
            for track in tracklist:
                newoutput += ('Track: %s\n' % track.name)
                self.log(track.name)
                if track.name == self.cf_vars[cf_id]['playing_track_name']:
                    newoutput += "THIS IS THE ONE\n"
                    t = track
                    playing_clip_index = t.playing_slot_index + 1
                    playing_clip_slot = t.clip_slots[t.playing_slot_index]
                    num_clips = len(t.clip_slots)
                    newoutput += ("PLAYING CLIP:" + playing_clip_slot.clip.name + "\n")
                    newoutput += "\nNUM CLIPS:" + str(num_clips)

        except Exception as e:
            self.log('\n\nERROR:\n')
            self.log(e)

        self.log("\n\nOutput:" + newoutput + '\n-----\n')

        if self.cf_vars[cf_id]['playing_track_name'] == self.cf_vars[cf_id]['right']:
            action_0 = '(RPSEQ) "' + args['left'] + '"/PLAY RND 1-' + playing_clip_index + ';"' + args['left'] + '"/PLAY RND ' + playing_clip_index + '-' + num_clips
            action = '"' + args['left'] + '"/WAIT 1;"' + args['left'] + '"/CLIP START RND song.view.detail_clip.loop_start-song.view.detail_clip.loop_end; WAIT 5; "' + args['right'] + '"/VOL RAMP 100 0; "' + args['left'] + '"/VOL RAMP 100 100;'
            self.cf_vars[cf_id]['playing_track_name'] = self.cf_vars[cf_id]['left']
            self.log(action_0)
        else:
            action_0 = '(RPSEQ) "' + args['right'] + '"/PLAY RND 1-' + playing_clip_index + ';"' + args['right'] + '"/PLAY RND ' + playing_clip_index + '-' + num_clips
            self.log(action_0)
            action = '"' + args['right'] + '"/WAIT 1;"' + args['right'] + '"/CLIP START RND song.view.detail_clip.loop_start-song.view.detail_clip.loop_end; WAIT 5; "' + args['right'] + '"/VOL RAMP 100 100; "' + args['left'] + '"/VOL RAMP 100 0;'
            self.cf_vars[cf_id]['playing_track_name'] = self.cf_vars[cf_id]['right']

        #self.canonical_parent.clyphx_pro_component.trigger_action_list(action_0)
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action)
        self.cf_vars[cf_id]['playing_track_name'] = self.cf_vars[cf_id]['playing_track_name'] if self.cf_vars[cf_id]['playing_track_name'] == self.cf_vars[cf_id]['left'] else self.cf_vars[cf_id]['right']

