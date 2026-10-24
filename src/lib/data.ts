/**
 * The JSON data files edited through Pages CMS (the Galerij der Koningen is a content
 * collection, see content.config.ts), validated at build time so a bad edit fails the
 * build (and the deploy) instead of silently breaking a page.
 */
import { z } from 'astro/zod';
import documentenJson from '../data/documenten.json';
import fotoarchiefJson from '../data/fotoarchief.json';
import siteJson from '../data/site.json';

export const DOC_SOORTEN = [
	'Programma kermis',
	'Uitnodiging rekening & verantwoording',
	'Notulen rekening & verantwoording',
	'Winterkostmaaltijd / overig',
] as const;

const document = z.object({
	jaar: z.number(),
	soort: z.enum(DOC_SOORTEN),
	bestand: z.string(),
	titel: z.string().optional(),
});

const archieffoto = z.object({
	foto: z.string().optional(),
	fotoKlein: z.string().optional(),
	bijschrift: z.string().optional(),
});

const site = z.object({
	naam: z.string(),
	omschrijving: z.string(),
	email: z.string().email(),
	bankrekening: z.string(),
	correspondentie: z.string(),
});

export const documenten = z.array(document).parse(documentenJson);
export const fotoarchief = z.array(archieffoto).parse(fotoarchiefJson);
export const siteInfo = site.parse(siteJson);
