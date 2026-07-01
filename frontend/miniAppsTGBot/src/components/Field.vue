<template>
    <div class="field">
        <input
        class="InputField"
        type="text"
        :placeholder="placeholder"
        v-model="model"
        >
    </div>
</template>

<script setup>
const model = defineModel({ type: String, default: ''})

defineProps({
    placeholder: {
        default: '',}
}) 
</script>

<style>
.InputField {
    border: solid 0.5px;
    border-radius: 3px;
    width: 100%;
    /* height: 10vw; */

    padding: 10px 15px;
    transition: 0.2s;

    :hover {
        border-color: #7aff8a;}
    &:focus {
        border-color: #7aff8a;
        box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
        outline: none;
    }
}
</style>