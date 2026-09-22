/**
 * SatQuery AI — API Service Client
 * Handles communication with the FastAPI backend orchestrator.
 */

export async function queryPipeline(files, queryText) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('images', file, file.name);
  }
  formData.append('query', queryText);

  const response = await fetch('/query', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.answer || `Pipeline execution failed (${response.status})`);
  }

  return await response.json();
}

export async function checkCompatibility(files, queryText) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('images', file, file.name);
  }
  formData.append('query', queryText);

  const response = await fetch('/compatibility-check', {
    method: 'POST',
    body: formData,
  });

  return await response.json();
}

export async function submitOperatorFeedback({ queryId, rating, notes, correctedBbox }) {
  const response = await fetch('/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query_id: queryId,
      rating,
      notes: notes || '',
      corrected_bbox: correctedBbox || null,
    }),
  });
  return await response.json();
}

export async function logSuggestionClick({ queryId, suggestionText, taskType }) {
  try {
    await fetch('/suggestion/click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query_id: queryId,
        suggestion_text: suggestionText,
        task_type: taskType,
      }),
    });
  } catch (e) {
    console.warn('Failed to log suggestion click:', e);
  }
}

export async function fetchHealth() {
  const res = await fetch('/health');
  return await res.json();
}
