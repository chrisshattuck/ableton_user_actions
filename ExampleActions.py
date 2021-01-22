# Import UserActionsBase to extend it.
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
import random

class ExampleActions(UserActionsBase):

    def create_actions(self):
        self.add_global_action('crossfade_random', self.crossfade_random)
        self.cf_vars = {}
        self.log_message = ''

    # Converts arguments in the form of "key=value,key=value"
    # to a dictionary.
    def prepare_args(self, args):
        args = args.split(",")
        new_args = {}
        for k, v in enumerate(args):
            arg_parts = v.split('=')
            new_args[arg_parts[0]] = arg_parts[1].strip('"\'')
        return new_args

    def log(self, message):
        self.log_message += '\n\n' + message + '\n\n'

    def output_log(self):
        self.canonical_parent.log_message(self.log_message)

    def run_action(self, action):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action)

    def prepare_action(self, action_list):
        return ';'.join(action_list)

    # TODO: If working between two tracks that aren't identical, this won't work. But it could.
    def crossfade_random(self, action_def, args):

        args = self.prepare_args(args)
        cf_id = args['track']
        tracklist = list(self.song().tracks)  # Type as list, won't work otherwise

        # Initialize crossfade
        if not cf_id in self.cf_vars:
            self.cf_vars[cf_id] = args  # Process arguments from x-action

            # Duplicate track if not duplicated
            dupe_track_name = self.cf_vars[cf_id]['track'] + ' (COPY)'
            self.cf_vars[cf_id]['dupe'] = dupe_track_name
            duplicate_exists = False
            for track in tracklist:
                if track.name == dupe_track_name:
                    duplicate_exists = True
            rename_next = False

            if not duplicate_exists:
                self.run_action('"' + self.cf_vars[cf_id]['track'] + '"/ DUPE')
                tracklist = list(self.song().tracks)
                rename_next = False
                for i, track in enumerate(tracklist):

                    if rename_next:
                        rename_next = False
                        track_index = i + 1
                        self.run_action(str(track_index) + '/ NAME "' + dupe_track_name + '"')
                        break
                    if track.name == self.cf_vars[cf_id]['track']:
                        rename_next = True

            self.cf_vars[cf_id]['playing_track_name'] = self.cf_vars[cf_id]['dupe']  # Set default playing
            action_list = [
                '"' + self.cf_vars[cf_id]['track'] + '"/ VOL 0',
                '"' + self.cf_vars[cf_id]['dupe'] + '"/ VOL 0',
            ]
            action = self.prepare_action(action_list)
            self.run_action('WAIT 5; "' + self.cf_vars[cf_id]['track'] + '"/ VOL 0')
            self.run_action('WAIT 5; "' + self.cf_vars[cf_id]['dupe'] + '"/ VOL 0')
            self.log(action)
        # End initialize

        current_track = self.cf_vars[cf_id]['track']
        next_track = self.cf_vars[cf_id]['dupe']
        if self.cf_vars[cf_id]['playing_track_name'] == self.cf_vars[cf_id]['dupe']:
            current_track = self.cf_vars[cf_id]['dupe']
            next_track = self.cf_vars[cf_id]['track']

        # Loop through tracks to find currently playing one
        for track in tracklist:
            if track.name == self.cf_vars[cf_id]['playing_track_name']:
                # Need to loop through and find clip slots with clips
                num_clips = 0
                for slot in track.clip_slots:
                    if slot.has_clip:
                        num_clips += 1
                if track.playing_slot_index == -2:  # -2 if there's no currently playing track
                    playing_clip_index = random.randint(1, num_clips)
                else:
                    playing_clip_index = track.playing_slot_index + 1

                # Generate action for playing a random clip that is not
                # the currently playing one and that is within the range
                # of actual clips, not just slots.
                playing_clip_index_before = playing_clip_index - 1
                playing_clip_index_after = playing_clip_index + 1
                action_before_clip = '"' + next_track + '"/PLAY RND 1-' + str(playing_clip_index_before) + ';'
                action_after_clip = '"' + next_track + '"/PLAY RND ' + str(playing_clip_index_after) + '-' + str(num_clips)
                # Will crash if it's 0 or more than the number of clips in track
                wait = '(RPSEQ) '
                if playing_clip_index_before < 1:
                    action_before_clip = ''
                    wait = 'WAIT 3; '
                if playing_clip_index_after >= num_clips:
                    action_after_clip = ''
                    wait = 'WAIT 3; '
                action_play_random = wait + action_before_clip + action_after_clip
                self.log('PLAY RANDOM:' + action_play_random)

        # Generate action for changing the loop start time and
        # performing crossfade.
        action_list = [
            'WAIT 2',
            '"' + next_track + '"/CLIP START RND song.view.detail_clip.loop_start-song.view.detail_clip.loop_end',
            'WAIT 4',
            '"' + current_track + '"/VOL RAMP 100 0',
            '"' + next_track + '" / VOL RAMP 100 100',
        ]
        action = self.prepare_action(action_list)
        self.run_action(action_play_random)
        self.run_action(action)

        self.cf_vars[cf_id]['playing_track_name'] = next_track

        self.output_log()

