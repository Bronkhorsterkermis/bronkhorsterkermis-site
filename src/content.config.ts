import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

/** Ordinary pages. `bijlage` appends a structured-data section rendered by the template. */
const pages = defineCollection({
	loader: glob({ pattern: '*.md', base: './src/content/pages' }),
	schema: z.object({
		titel: z.string(),
		volgorde: z.number().default(99),
		inMenu: z.boolean().default(true),
		bijlage: z.enum(['kermisjaren', 'documenten', 'koningen', 'fotoarchief']).optional(),
		/** Page id on the old PHP site; used to generate redirects from /4, /index.php?page=4 etc. */
		legacyId: z.number().optional(),
	}),
});

/** One entry per kermis year, shown newest-first on the home page. */
const jaren = defineCollection({
	loader: glob({ pattern: '*.md', base: './src/content/jaren' }),
	schema: z.object({
		jaar: z.number(),
		fotoalbum: z.string().url().optional(),
		items: z
			.array(
				z.object({
					foto: z.string().optional(),
					bijschrift: z.string().optional(),
				}),
			)
			.default([]),
	}),
});

export const collections = { pages, jaren };
