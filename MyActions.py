# Import UserActionsBase to extend it.
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
import random

class MyActions(UserActionsBase):

    def create_actions(self):
        self.add_global_action('crossfade_random', self.crossfade_random)
        self.cf_vars = {}
        self.log_message = ''
        self.initialized = []
        self.call_count = 0

    # Converts arguments in the form of "key=value,key=value"
    # to a dictionary.
    def prepare_args(self, args, default_args={}):
        args = args.split(",")
        new_args = {}
        for k, v in enumerate(args):
            arg_parts = v.split('=')
            new_args[arg_parts[0]] = arg_parts[1].strip('"\'').strip()
        for k, v in default_args.items():
            if k not in new_args:
                new_args[k] = v
        return new_args

    # Keep ongoing log string.
    def log(self, message):
        self.log_message += '\n\n' + message + '\n\n'

    # Output the log string.
    def output_log(self):
        self.canonical_parent.log_message(self.log_message)
        self.log_message = ''

    # Shortcut for triggering action.
    def run_action(self, action):
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action)

    def run_action_list(self, action_list):
        action = self.prepare_action(action_list)
        self.run_action(action)

    # Takes list and concatenates it into an action list.
    def prepare_action(self, action_list):
        return ';'.join(action_list)

    # Randomly crossfades between two tracks.
    #
    # Uses the following arguments:
    # - track="Name of track"
    # - fadetime=100 (defaults to 100)
    # Does the following:
    # - Duplicates the track.
    # - Sets the volume of original and duplicated track to 0.
    # - Selects a random clip in the original track,
    #    sets a random start time within the range of
    #    the clip's loop.
    # - Plays the clip.
    # - Fades the clip in.
    # - The next time the x-clip plays, it will select
    #   a random cip from the duplicated track, fade it
    #   in and fade out the original.
    # - Subsequent plays repeat the random crossfade.
    # For this to work right, ensure the following:
    # - Clips should be set to loop.
    # - Clips in the duplicated track should be
    #   identical to the original.
    # - To repeat this, set it on a looping clip and use
    #   (LSEQ), as in:
    #   [] (LSEQ) crossfade_random track="Name of track"
    def crossfade_random(self, action_def, args):
        default_args = {
            'fadetime': 100
        }
        args = self.prepare_args(args, default_args)
        cf_id = args['track']
        tracklist = list(self.song().tracks)  # Type as list, won't work otherwise

        self.call_count += 1

        # Reset passed args
        if cf_id in self.cf_vars:
            for key, value in args.items():
                self.cf_vars[cf_id][key] = value

        # Run first time this runs on a track
        else:
            self.cf_vars[cf_id] = args  # Process arguments from x-action

            # Duplicate track if not duplicated
            self.cf_vars[cf_id]['dupe'] = self.cf_vars[cf_id]['track'] + ' (COPY)'
            duplicate_exists = False
            for track in tracklist:
                if track.name == self.cf_vars[cf_id]['dupe']:
                    duplicate_exists = True

            if not duplicate_exists:
                self.run_action('"' + self.cf_vars[cf_id]['track'] + '"/ DUPE')
                # Regenerate track list including duplicate
                tracklist = list(self.song().tracks)
                rename_next = False
                for i, track in enumerate(tracklist):
                    if rename_next:
                        rename_next = False
                        track_index = i + 1
                        self.run_action(str(track_index) + '/ NAME "' + self.cf_vars[cf_id]['dupe'] + '"')
                        break
                    if track.name == self.cf_vars[cf_id]['track']:
                        rename_next = True
            # Set default playing track
            self.cf_vars[cf_id]['playing_track_name'] = self.cf_vars[cf_id]['dupe']
            # Set volume on both tracks to 0
            action_list = [
                'WAIT 5',
                '"' + self.cf_vars[cf_id]['track'] + '"/ VOL 0',
                '"' + self.cf_vars[cf_id]['dupe'] + '"/ VOL 0',
            ]
            self.run_action_list(action_list)
        # End initialize

        # Set the current and next tracks.
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

        if not 'fadetime' in args:
            self.cf_vars[cf_id]['fadetime'] = 100

        # Generate action for changing the loop start time and
        # performing crossfade.
        action_list = [
            'WAIT 2',
            '"' + next_track + '"/CLIP START RND song.view.detail_clip.loop_start-song.view.detail_clip.loop_end',
            'WAIT 4',
            '"' + current_track + '"/VOL RAMP ' + str(self.cf_vars[cf_id]['fadetime']) + ' 0',
            '"' + next_track + '" / VOL RAMP ' + str(self.cf_vars[cf_id]['fadetime']) + ' 100',
        ]
        self.run_action_list(action_list)

        self.cf_vars[cf_id]['playing_track_name'] = next_track

        self.output_log()