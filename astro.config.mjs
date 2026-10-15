// @ts-check
import { defineConfig } from 'astro/config';
import remarkMedia from './src/lib/remark-media.mjs';

// https://astro.build/config
export default defineConfig({
	site: 'https://www.bronkhorsterkermis.nl',
	// Emit activiteiten.html rather than activiteiten/index.html: Netlify then serves
	// /activiteiten directly instead of 301-redirecting it to /activiteiten/.
	build: { format: 'file' },
	trailingSlash: 'never',
	markdown: {
		remarkPlugins: [remarkMedia],
	},
});
