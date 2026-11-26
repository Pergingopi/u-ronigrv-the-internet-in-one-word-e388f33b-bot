#!/usr/bin/env python3
"""One word for the whole internet.

The program's only job: write a single word into
``$MAKEFUN_OUTPUT_DIR/entry.txt`` (default ``/output/entry.txt``).

The word is fixed: "Enshittification". There is no network access, no
randomness and no clock involved, so every invocation produces
byte-identical output. The word is checked against the bounty gate
before anything is written; the publish step is atomic (a temporary file
staged inside the output directory, then ``os.replace``), fsynced, set
to mode 0644 and read back for verification.
"""

import os
import sys
import unicodedata

# The bounty gate: 1-30 characters, exactly ONE word of letters only.
LOWER_BOUND = 1
UPPER_BOUND = 30

WORD = "Enshittification"


def _forbidden_reason(ch):
    """Why *ch* may not appear in an entry, or None when it may.

    Rejects the byte-order mark, C1 controls, line/paragraph separators,
    surrogates, every invisible or control category, tabs and any space
    that is not the plain ASCII space.
    """
    code = ord(ch)
    if ch == "\ufeff":
        return "BOM (U+FEFF) is not allowed"
    if 0x80 <= code <= 0x9F:
        return "C1 control character U+%04X is not allowed" % code
    if code in (0x2028, 0x2029):
        return "line/paragraph separator U+%04X is not allowed" % code
    if 0xD800 <= code <= 0xDFFF:
        return "surrogate U+%04X is not allowed" % code
    if unicodedata.category(ch) in ("Cc", "Cf", "Cs", "Co", "Cn"):
        return "invisible/control character U+%04X is not allowed" % code
    if unicodedata.category(ch) == "Zs" and code != 0x20:
        return "non-breaking/other space U+%04X is not allowed" % code
    if ch == "\t":
        return "tab is not allowed"
    return None


def _check_shape(text):
    """Reject entries that fail the size, blankness or single-line rules."""
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if not text or not text.strip():
        raise ValueError("entry is empty or whitespace-only")
    if text != text.strip():
        raise ValueError("entry has leading or trailing whitespace")
    if len(text) < LOWER_BOUND or len(text) > UPPER_BOUND:
        raise ValueError(
            "entry is %d characters, gate is %d-%d"
            % (len(text), LOWER_BOUND, UPPER_BOUND)
        )
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")


def _check_single_word(text):
    """Reject anything that is not exactly one word of letters only."""
    if not text.isalpha():
        raise ValueError("entry must be exactly one word (letters only)")


def _check_characters(text):
    """Reject entries containing any forbidden character."""
    for ch in text:
        reason = _forbidden_reason(ch)
        if reason is not None:
            raise ValueError(reason)


def check_entry(text):
    """Raise ValueError unless *text* passes this bounty's gate."""
    _check_shape(text)
    _check_single_word(text)
    _check_characters(text)


def output_directory():
    """Resolve the output directory from the environment."""
    directory = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not directory or "\x00" in directory:
        raise ValueError("invalid MAKEFUN_OUTPUT_DIR")
    return directory


def empty_output_directory(path):
    """Delete everything inside *path* without deleting *path* itself.

    The grader bind-mounts this directory, so removing the mount point
    would fail; only its contents are cleared.
    """
    os.makedirs(path, exist_ok=True)
    for name in os.listdir(path):
        full = os.path.join(path, name)
        if os.path.isdir(full) and not os.path.islink(full):
            for sub in os.listdir(full):
                os.unlink(os.path.join(full, sub))
            os.rmdir(full)
        else:
            os.unlink(full)


def _sync_directory(path):
    """Fsync a directory on a best-effort basis (rename durability)."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _sweep_stale_staging(out_dir):
    """Remove leftover staging files from earlier interrupted runs."""
    for name in os.listdir(out_dir):
        if name.startswith(".entry-") and name.endswith(".tmp"):
            try:
                os.unlink(os.path.join(out_dir, name))
            except OSError:
                pass


def publish_atomically(text, out_dir):
    """Publish *text* as entry.txt inside *out_dir*, atomically.

    The temporary file lives in the output directory itself, so the
    rename stays on one filesystem even when that directory is a
    bind-mount. The file is fsynced, chmodded 0644, swapped in with
    ``os.replace`` and read back to prove the bytes landed.
    """
    _sweep_stale_staging(out_dir)
    target = os.path.join(out_dir, "entry.txt")
    staging = os.path.join(out_dir, ".entry-%d.tmp" % os.getpid())
    if os.path.exists(staging):
        os.unlink(staging)
    payload = text.encode("utf-8")
    fd = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        count = os.write(fd, payload)
        if count != len(payload):
            raise OSError("short write: %d of %d bytes" % (count, len(payload)))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(staging, 0o644)
    os.replace(staging, target)
    os.chmod(target, 0o644)
    _sync_directory(out_dir)
    with open(target, "rb") as handle:
        written_back = handle.read()
    if written_back != payload:
        raise OSError("read-back mismatch after publish")
    if oct(os.stat(target).st_mode & 0o777) != "0o644":
        raise OSError("entry.txt mode is not 0644")
    return target


def run():
    check_entry(WORD)
    directory = output_directory()
    empty_output_directory(directory)
    target = publish_atomically(WORD, directory)
    print("wrote %s (%d chars)" % (target, len(WORD)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
