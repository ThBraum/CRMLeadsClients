/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: "class",
	content: [
		"./templates/**/*.html",
		"./crm/templates/**/*.html",
		"./dashboard/templates/**/*.html",
		"./static/js/**/*.js",
	],
	theme: {
		extend: {
			fontFamily: {
				sans: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
			},
		},
	},
	plugins: [],
};
