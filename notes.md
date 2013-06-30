the entire forest is tagged with a topic
tree s/t one root to leaf traversal is a unique sentence
leaf nodes include "tags": personality indicator for the sentence
edge to responses by AI personality, then by mood
at the end of the sentence, follow edge corresponding to the current AI type
responses are per topic-sentence ('what's it about' - movies vs books)
word replacement

input a bunch of sentences
build a forest of trees from those sentences
this all gets written to XML (or other hierarchical format)

intro - load existing topic or start new
ls - show current tree
new sentence - input sentence
    tag should be x
new response - input sentence
    mood should be x
    character type should be x
player sentences should have unique IDs
response ID chartype mood next_topic text
    mood, chartype support listing,glob character
sentence tag text
