#!/bin/bash
set -u
DOSSIER="${1:-.}"
MODELE="gemma4:12b-mlx"
LANGUE_RESUME="English"
SORTIE="$DOSSIER/resumes"
mkdir -p "$SORTIE"

tmp_txt=$(mktemp); tmp_prompt=$(mktemp); tmp_payload=$(mktemp)
trap 'rm -f "$tmp_txt" "$tmp_prompt" "$tmp_payload"' EXIT

# --- Vérifications préalables ---
if ! curl -s --max-time 3 http://localhost:11434/api/tags >/dev/null; then
  echo "❌ Ollama ne répond pas. Lancez : ollama serve (ou ouvrez l'application)"; exit 1
fi
if ! curl -s http://localhost:11434/api/tags | jq -e --arg m "$MODELE" '.models[]? | select(.name == $m)' >/dev/null; then
  echo "❌ Modèle '$MODELE' introuvable. Modèles installés :"
  curl -s http://localhost:11434/api/tags | jq -r '.models[].name'
  echo "   → Lancez : ollama pull $MODELE"
  exit 1
fi

# --- Boucle de résumé ---
for f in "$DOSSIER"/*; do
  case "$f" in
    *.pdf)              pdftotext "$f" "$tmp_txt" 2>/dev/null ;;
    *.doc|*.docx|*.rtf) textutil -convert txt -output "$tmp_txt" "$f" 2>/dev/null ;;
    *.txt|*.md)         cat "$f" > "$tmp_txt" ;;
    *) continue ;;
  esac

  if ! [ -s "$tmp_txt" ]; then
    echo "⚠️  Aucun texte extrait : $(basename "$f")"
    continue
  fi

  {
    printf 'You are a document summarization assistant. Summarize the following document in %s, using at most 10 bullet points. Keep technical terms, names and figures exactly as written in the source.\n\nDocument:\n' "$LANGUE_RESUME"
    cat "$tmp_txt"
  } > "$tmp_prompt"

  jq -n --arg m "$MODELE" --rawfile p "$tmp_prompt" \
    '{model:$m, prompt:$p, stream:false, options:{num_ctx:8192}}' > "$tmp_payload"

  reponse=$(curl -s http://localhost:11434/api/generate -d @"$tmp_payload")

  if echo "$reponse" | jq -e '(.error // null) == null' >/dev/null 2>&1; then
    echo "$reponse" | jq -r '.response // empty' > "$SORTIE/$(basename "$f").resume.txt"
    echo "✅ $(basename "$f")"
  else
    echo "❌ $(basename "$f") → $(echo "$reponse" | jq -r '.error // "réponse illisible"')"
  fi
done
