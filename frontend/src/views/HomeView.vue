<script setup>
import HomeCard from '../components/HomeCard.vue';
import { useFastStore } from '../stores/fast'
import { storeToRefs } from 'pinia'

const useFast = useFastStore()
const {msg, songs} = storeToRefs(useFast)

useFast.touchFast()
useFast.getHomeSongs()

</script>

<template>
    <div class="p-8">
        <button
            type="button"
            class="text-white text-2xl font-semibold hover:underline cursor-pointer"
        >
            {{msg}}
        </button>

        <div class="py-1.5"></div>

        <div class="flex items-center">
            <HomeCard image="https://picsum.photos/id/30/300/300" title="Title is here" subTitle="Subtitle is here" />
            <HomeCard image="https://picsum.photos/id/45/300/300" title="Title is here" subTitle="Subtitle is here" />
            <HomeCard class="md:block hidden" image="https://picsum.photos/id/65/300/300" title="Title is here" subTitle="Subtitle is here" />
            <HomeCard class="lg:block hidden" image="https://picsum.photos/id/67/300/300" title="Title is here" subTitle="Subtitle is here" />
            <HomeCard class="xl:block hidden" image="https://picsum.photos/id/100/300/300" title="Title is here" subTitle="Subtitle is here" />
        </div>
    </div>

    <div class="p-8">
        <button
            type="button"
            class="text-white text-2xl font-semibold hover:underline cursor-pointer"
        >
        Recommended radio
        </button>

        <div class="py-1.5"></div>

        <div class="grid-container">
            <div class="grid-item" v-for="track in songs" :key="track">
                <HomeCard :image="track.ImageHref" :title="track.Name" :subTitle="track.Artist" />
            </div>
        </div>
    </div>
</template>

<style>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.grid-item {
  border-radius: 4px;
}
</style>