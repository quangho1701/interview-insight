import type { Config } from "tailwindcss";
import checkUiConfig from "../../packages/ui/tailwind.config";

const config: Config = {
    presets: [checkUiConfig],
    content: [
        "./src/**/*.{js,ts,jsx,tsx,mdx}",
        "../../packages/ui/src/**/*.{js,ts,jsx,tsx,mdx}" // Redundant if in preset, but safe
    ],
    theme: {
        extend: {},
    },
    plugins: [],
};
export default config;
