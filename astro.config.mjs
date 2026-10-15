// @ts-check
import { defineConfig } from 'astro/config';
import remarkMedia from './src/lib/remark-media.mjs';

// https://astro.build/config
export default defineConfig({
	site: 'https://www.bronkhorsterkermis.nl',
	markdown: {
		remarkPlugins: [remarkMedia],
	},
});
