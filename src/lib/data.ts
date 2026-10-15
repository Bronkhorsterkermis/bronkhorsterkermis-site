/**
 * The JSON data files edited through Pages CMS, validated at build time so a bad edit fails the
 * build (and the deploy) instead of silently breaking a page.
 */
import { z } from 'astro/zod';
import koningenJson from '../data/koningen.json';
import documentenJson from '../data/documenten.json';
import fotoarchiefJson from '../data/fotoarchief.json';
import siteJson from '../data/site.json';

export const DOC_SOORTEN = [
	'Programma kermis',
	'Uitnodiging rekening & verantwoording',
	'Notulen rekening & verantwoording',
	'Winterkostmaaltijd / overig',
] as const;

const koning = z.object({
	jaar: z.number(),
	/** Last year of a range, e.g. 1939–1944 without kermis. */
	tot: z.number().optional(),
	koning: z.string().optional(),
	foto: z.string().optional(),
	video: z.string().optional(),
	opmerking: z.string().optional(),
});

const document = z.object({
	jaar: z.number(),
	soort: z.enum(DOC_SOORTEN),
	bestand: z.string(),
	titel: z.string().optional(),
});

const archieffoto = z.object({
	foto: z.string().optional(),
	bijschrift: z.string().optional(),
});

const site = z.object({
	naam: z.string(),
	omschrijving: z.string(),
	email: z.string().email(),
	bankrekening: z.string(),
	correspondentie: z.string(),
});

export const koningen = z
	.array(koning)
	.parse(koningenJson)
	.sort((a, b) => b.jaar - a.jaar);
export const documenten = z.array(document).parse(documentenJson);
export const fotoarchief = z.array(archieffoto).parse(fotoarchiefJson);
export const siteInfo = site.parse(siteJson);
