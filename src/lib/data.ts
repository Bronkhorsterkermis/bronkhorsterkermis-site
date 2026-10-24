/**
 * The JSON data files edited through Pages CMS, validated at build time so a bad edit fails the
 * build (and the deploy) instead of silently breaking a page. The Galerij der Koningen and the
 * Activiteiten documents are content collections instead; see content.config.ts.
 */
import { z } from 'astro/zod';
import fotoarchiefJson from '../data/fotoarchief.json';
import siteJson from '../data/site.json';

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

export const fotoarchief = z.array(archieffoto).parse(fotoarchiefJson);
export const siteInfo = site.parse(siteJson);
