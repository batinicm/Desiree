import { defineStore } from 'pinia'

export const useSongStore = defineStore('song', {
  state: () => ({
    isPlaying: false,
    audio: null,
    currentArtist: null,
    currentTrack: null,
    masterTrack: null
  }),
  actions: {
    loadMasterSong(track){
        this.masterTrack = track
        this.loadSong(track)
    },

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

    async loadRecommendationInfo(masterTrack){
        let {data} = await axios.post('expandrecommendations', masterTrack.Recommended)
        masterTrack.Recommended = data
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

    prevSong() {
        if(this.masterTrack === null){
            return
        }

        index = this.masterTrack.Recommended.indexOf(this.currentTrack)
        if(index == 0){
            index = this.masterTrack.Recommended.length
        }
        this.currentTrack = this.masterTrack.Recommended[index - 1]

        this.loadSong(currentTrack)
    },

    nextSong() {
        if(this.masterTrack === null){
            return
        }

        index = this.masterTrack.Recommended.indexOf(this.currentTrack)
        if(index == (this.masterTrack.Recommended.length - 1)){
            this.masterTrack = this.masterTrack.Recommended[index]
            this.loadRecommendationInfo(this.masterTrack)
            index = -1
        }
        this.currentTrack = this.masterTrack.Recommended[index + 1]

        this.loadSong(currentTrack)
    },

    playFromFirst() {
        this.resetState()
        this.loadSong(this.masterTrack)
    },

    resetState() {
        this.isPlaying = false
        this.audio = null
        this.currentArtist = null
        this.currentTrack = null
        this.masterTrack = null
    }
  },
  persist: true
})
