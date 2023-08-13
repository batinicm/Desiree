import { defineStore } from 'pinia'

export const useSongStore = defineStore('song', {
  state: () => ({
    isPlaying: false,
    audio: null,
    currentArtist: null,
    currentTrack: null
  }),
  actions: {
    loadSong(track) {
        this.currentArtist = track.Artist
        this.currentTrack = track

        if (this.audio && this.audio.src) {
            this.audio.pause()
            this.isPlaying = false
            this.audio.src = ''
        }

        this.audio = new Audio(track.Url)

        setTimeout(() => {
            this.isPlaying = true
            this.audio.play()
        }, 200)
    },

    playOrPauseSong() {
        if (this.audio.paused) {
            this.isPlaying = true
            this.audio.play()
        } else {
            this.isPlaying = false
            this.audio.pause()
        }
    },

    playOrPauseThisSong(track) {
        if (!this.audio || !this.audio.src || (this.currentTrack.Name !== track.Name)) {
            this.loadSong(track)
            return
        }

        this.playOrPauseSong()
    },

    prevSong(currentTrack) {
        this.loadSong(currentTrack)
    },

    nextSong(currentTrack) {
        /**if (currentTrack.id === artist.tracks.length) {
            let track = artist.tracks[0]
            this.loadSong(artist, track)
        } else {
            let track = artist.tracks[currentTrack.id]
            this.loadSong(artist, track)
        }
        **/
    },

    playFromFirst() {
        /**
        this.resetState()
        let track = artist.tracks[0]
        this.loadSong(artist, track)
         */
    },

    resetState() {
        this.isPlaying = false
        this.audio = null
        this.currentArtist = null
        this.currentTrack = null
    }
  },
  persist: true
})
