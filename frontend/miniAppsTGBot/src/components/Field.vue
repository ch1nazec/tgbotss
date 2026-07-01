<template>
    <div class="field">
        <input
        class="InputField"
        type="text"
        :placeholder="placeholder"
        >
    </div>
</template>

<script>
export default {
    name: 'Field',
    props: {
        placeholder: {
            type: [String],
            default: ''
        }
    }
}
</script>

<style>
.InputField {
    border: none;
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