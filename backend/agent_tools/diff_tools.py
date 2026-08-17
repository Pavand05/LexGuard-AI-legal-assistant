"""
Contract Redlining & Visual Diff Engine
Produces structured clause-level additions, removals, and replacements.
"""
import difflib
from typing import Dict, Any, List


def compute_clause_diff(original_text: str, proposed_text: str) -> Dict[str, Any]:
    """
    Compute fine-grained word and line diffs between original clause and proposed redline.
    Returns:
      diff_html: Styled HTML representation with <ins> and <del> tags.
      stats: {added_words: int, removed_words: int, unchanged_words: int}
      has_changes: bool
    """
    orig_words = original_text.split()
    prop_words = proposed_text.split()
    
    matcher = difflib.SequenceMatcher(None, orig_words, prop_words)
    diff_chunks = []
    added_count = 0
    removed_count = 0
    unchanged_count = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            chunk = " ".join(orig_words[i1:i2])
            diff_chunks.append(f"<span class='text-slate-300'>{chunk}</span>")
            unchanged_count += (i2 - i1)
        elif tag == 'insert':
            chunk = " ".join(prop_words[j1:j2])
            diff_chunks.append(f"<ins class='bg-emerald-950/70 text-emerald-300 border-b border-emerald-500 font-semibold px-1 rounded mx-0.5'>{chunk}</ins>")
            added_count += (j2 - j1)
        elif tag == 'delete':
            chunk = " ".join(orig_words[i1:i2])
            diff_chunks.append(f"<del class='bg-red-950/70 text-red-400 line-through px-1 rounded mx-0.5 opacity-80'>{chunk}</del>")
            removed_count += (i2 - i1)
        elif tag == 'replace':
            del_chunk = " ".join(orig_words[i1:i2])
            ins_chunk = " ".join(prop_words[j1:j2])
            diff_chunks.append(f"<del class='bg-red-950/70 text-red-400 line-through px-1 rounded mx-0.5 opacity-80'>{del_chunk}</del>")
            diff_chunks.append(f"<ins class='bg-emerald-950/70 text-emerald-300 border-b border-emerald-500 font-semibold px-1 rounded mx-0.5'>{ins_chunk}</ins>")
            removed_count += (i2 - i1)
            added_count += (j2 - j1)

    return {
        "diff_html": " ".join(diff_chunks),
        "added_words": added_count,
        "removed_words": removed_count,
        "unchanged_words": unchanged_count,
        "has_changes": added_count > 0 or removed_count > 0
    }
