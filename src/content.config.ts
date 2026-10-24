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
					/** Optional own crop shown on the page; `foto` is what the lightbox enlarges. */
					fotoKlein: z.string().optional(),
					bijschrift: z.string().optional(),
				}),
			)
			.default([]),
	}),
});

/** Galerij der Koningen: one file per year (or per period without kermis, e.g. 1939–1944). */
const koningen = defineCollection({
	loader: glob({ pattern: '*.{yml,yaml}', base: './src/content/koningen' }),
	schema: z.object({
		jaar: z.number(),
		/** Last year of a range, e.g. 1939–1944 without kermis. */
		tot: z.number().optional(),
		koning: z.string().optional(),
		foto: z.string().optional(),
		/** Optional own crop shown in the gallery; `foto` is what the lightbox enlarges. */
		fotoKlein: z.string().optional(),
		video: z.string().optional(),
		opmerking: z.string().optional(),
	}),
});

/** Activiteiten: one file per year with that year's documents (paths under /downloads). */
const documenten = defineCollection({
	loader: glob({ pattern: '*.{yml,yaml}', base: './src/content/documenten' }),
	schema: z.object({
		jaar: z.number(),
		programma: z.string().optional(),
		uitnodiging: z.string().optional(),
		notulen: z.string().optional(),
		overig: z
			.array(z.object({ titel: z.string().optional(), bestand: z.string() }))
			.default([]),
	}),
});

export const collections = { pages, jaren, koningen, documenten };
