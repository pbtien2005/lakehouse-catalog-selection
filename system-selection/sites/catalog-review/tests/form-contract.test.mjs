import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as core from '../dist/core.js';

test('UI payload is restricted to canonical v2 IDs; old fixture fields are absent', async () => {
  assert.equal(typeof core.buildPayload, 'function');
  const registry = JSON.parse(await readFile('../../research/catalog-knowledge-base/form-v2-registry.json','utf8'));
  const payload = core.buildPayload({I01:'aws',I02:['spark'],I03:'iceberg',operations:'nice',portability:'important',storage:'S3'},registry);
  assert.deepEqual(payload,{form_revision:'input-v2',answers:{I01:'aws',I02:['spark'],I03:'iceberg'}});
});

test('UI does not export a second decision engine', () => {
  assert.equal(core.evaluate, undefined);
});
