/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["../**/*.{html,js,py}"], // .py because django forms.py files could contain tailwind classes
    theme: {
        extend: {
            colors: {
                "primary": "#000000",
                "dv_green": "#28b400",
                "dv_red": "#ff0000",
                "dv_white": "#ffffff"
            },
            fontFamily: {
                'faruma': ['faruma'],
                'sangu': ['sangu',]
            },
        },
    },
    plugins: [],
}



