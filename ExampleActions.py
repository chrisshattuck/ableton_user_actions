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
        self.canonical_parent.log_message(message)

    def run_action(self, action):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(run_action)

    # TODO: If working between two tracks that aren't identical, this won't work. But it could.
    def crossfade_random(self, action_def, args):

        args = self.prepare_args(args)
        cf_id = args['left'] + args['right']
        tracklist = list(self.song().tracks)  # Type as list, won't work otherwise

        # Initialize crossfade
        if not cf_id in self.cf_vars:
            self.cf_vars[cf_id] = args  # Process arguments from x-action

            # Duplicate track if not duplicated
            dupe_track_name = args['left'] + ' (COPY)'
            duplicate_exists = False
            for track in tracklist:
                if track.name == dupe_track_name:
                    duplicate_exists = True
            if not duplicate_exists:


            self.cf_vars[cf_id]['playing_track_name'] = args['left'] # Set default playing
            action = '"' + args['left'] + '"/ VOL 0;"' + args['right'] + '"/ VOL 0'
            self.canonical_parent.clyphx_pro_component.trigger_action_list(action)

        newoutput = ''

        current_track = self.cf_vars[cf_id]['left']
        next_track = self.cf_vars[cf_id]['right']
        if self.cf_vars[cf_id]['playing_track_name'] == self.cf_vars[cf_id]['right']:
            current_track = self.cf_vars[cf_id]['right']
            next_track = self.cf_vars[cf_id]['left']

        try:
            # Loop through tracks to find currently playing one
            for track in tracklist:
                if track.name == self.cf_vars[cf_id]['playing_track_name']:
                    newoutput += "THIS IS THE ONE\n"
                    num_clips = len(track.clip_slots)
                    playing_clip_index = track.playing_slot_index + 1
                    playing_clip_index_before = playing_clip_index - 1
                    playing_clip_index_after = playing_clip_index + 1
                    action_before_clip = '"' + next_track + '"/PLAY RND 1-' + str(playing_clip_index_before) + ';'
                    action_after_clip = '"' + next_track + '"/PLAY RND ' + str(playing_clip_index_after) + '-' + str(num_clips)
                    # Will crash if it's 0 or more than the number of clips in track
                    if playing_clip_index_before < 1:
                        action_before_clip = ''
                    if playing_clip_index_after == num_clips:
                        action_after_clip = ''
                    action_0 = '(RPSEQ) ' + action_before_clip + action_after_clip

                    # Could be helpful later
                    # playing_clip_slot = track.clip_slots[track.playing_slot_index]

        except Exception as e:
            self.log('\n\nERROR:\n')
            self.log(e)

        self.log("\n\nOutput:" + newoutput + '\n-----\n')


        action = 'WAIT 1;"' + next_track + '"/CLIP START RND song.view.detail_clip.loop_start-song.view.detail_clip.loop_end; WAIT 5; "' + current_track + '"/VOL RAMP 100 0; "' + next_track + '"/VOL RAMP 100 100;'
        self.cf_vars[cf_id]['playing_track_name'] = next_track

        self.run_action(action_0)
        self.run_action(action)
        self.cf_vars[cf_id]['playing_track_name'] = self.cf_vars[cf_id]['playing_track_name'] if self.cf_vars[cf_id]['playing_track_name'] == self.cf_vars[cf_id]['left'] else self.cf_vars[cf_id]['right']

