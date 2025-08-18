import os
import shutil
import tempfile
import pytest
from src.chroma_interface import ChromaCorpus

TEST_API_KEY = os.getenv("OPENAI_API_KEY") or "sk-xxxx"  # set a dummy/fake key if using mocks

@pytest.fixture
def temp_chroma_dir():
    """Creates a temporary directory and cleans up after."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_create_and_count_empty(temp_chroma_dir):
    corpus = ChromaCorpus(
        chroma_dir=temp_chroma_dir,
        collection_name="test_collection",
        openai_api_key=TEST_API_KEY,
        mode="create"
    )
    assert corpus.count_documents() == 0

def test_add_and_retrieve(temp_chroma_dir):
    corpus = ChromaCorpus(
        chroma_dir=temp_chroma_dir,
        collection_name="test_collection",
        openai_api_key=TEST_API_KEY,
        mode="create"
    )
    texts = ["The Amazon basin has several cave systems."]
    metadatas = [{"source": "test"}]
    corpus.add_texts(texts, metadatas)

    assert corpus.count_documents() == 1
    results = corpus.get_relevant_chunks("cave systems in Amazon")
    assert isinstance(results, list)
    assert len(results) > 0
    assert hasattr(results[0], "page_content")

def test_reset_mode(temp_chroma_dir):
    # Fill with some data
    corpus = ChromaCorpus(
        chroma_dir=temp_chroma_dir,
        collection_name="test_collection",
        openai_api_key=TEST_API_KEY,
        mode="create"
    )
    corpus.add_texts(["Test doc"], [{"source": "reset-test"}])
    assert corpus.count_documents() == 1

    # Now reset
    corpus_reset = ChromaCorpus(
        chroma_dir=temp_chroma_dir,
        collection_name="test_collection",
        openai_api_key=TEST_API_KEY,
        mode="reset"
    )
    assert corpus_reset.count_documents() == 0

