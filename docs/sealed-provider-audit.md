# One-use encrypted inventory delivery

An owner-authorized alternative when the coding integration can write reviewed
workflows but cannot create repository Secrets. This does not grant Secrets API
access, persist a credential configuration, or verify zero-cost generation.

1. A reviewed main-branch change to `sealed-run-request.json` starts an
   inventory-only job. Its delivery ref must be the current Arena session branch.
2. The runner generates a new RSA-3072 key and publishes only its public key and
   job-bound challenge as a check annotation. The private key is temporarily
   stored with mode 0600 in RUNNER_TEMP, outside the artifact directory.
3. The sender verifies the challenge came from the intended GitHub job, then
   encrypts the credential mapping using AES-256-GCM and wraps the AES key using
   RSA-OAEP-SHA256. The job ID, repository, and random challenge are authenticated
   associated data. No plaintext credential file is required on the sender.
4. Only this encrypted envelope is pushed as `sealed-request.json` on the fixed
   delivery branch. It is public ciphertext, not a reusable plaintext Secret.
   The runner waits at most ten minutes. Another job cannot decrypt it; modifying
   the ciphertext or context fails authentication.
5. The runner deletes its temporary key file before waiting, retaining the key
   only in process memory. It decrypts in memory, forces inventory mode with an
   empty generation policy, and never writes credentials into reports.
6. Sanitized reports are available as a one-day artifact and compressed check
   annotations. Those reports are PUBLIC; they must not contain account identity,
   raw API bodies, or credentials. The transport never publishes raw exceptions.
7. Delete the envelope from the branch after completion. Ciphertext remains in
   Git history. The private key must never be committed, uploaded, or returned.
   Runner teardown removes remaining process memory; Python cannot guarantee
   explicit in-memory zeroization. This is not a persistent secret vault.

Trust boundary: GitHub-hosted runner, repository workflow maintainers, the
credential sender, standard cryptography package and workflow dependencies.
Compromise of those components during the run can expose credentials, just as
with ordinary CI secrets. Use least-privilege, revocable provider keys. Rotate
keys already pasted into a conversation. No Google Drive upload or public
plaintext link is used. Inventory is not an inference, billing or voice test.

Tests cover round-trip encryption, ciphertext authentication, job replay
rejection, authenticated context and forbidden environment-variable injection.
