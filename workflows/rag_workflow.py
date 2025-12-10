"""LangGraph workflow for the RAG pipeline."""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

from models import Document, Chunk, EmbeddedChunk
from interfaces import IRepositoryReader, IDocumentChunker, IEmbeddingService, IVectorStore, ILocalFileReader


class RAGState(TypedDict):
    """State for the RAG workflow."""
    repository_url: str
    repo_path: str
    local_data_dir: str
    process_local_files: bool
    skip_existing_documents: bool
    force_reprocess: bool
    documents: List[Document]
    chunks: List[Chunk]
    embedded_chunks: List[EmbeddedChunk]
    error: str
    status: str
    existing_file_paths: set
    skipped_count: int
    new_count: int


class RAGWorkflow:
    """LangGraph workflow for processing documents and creating embeddings."""

    def __init__(
        self,
        repository_reader: IRepositoryReader,
        document_chunker: IDocumentChunker,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStore,
        local_file_reader: Optional[ILocalFileReader] = None
    ):
        """
        Initialize the RAG workflow.

        Args:
            repository_reader: Service for reading repositories
            document_chunker: Service for chunking documents
            embedding_service: Service for creating embeddings
            vector_store: Service for storing embeddings
            local_file_reader: Optional service for reading local files
        """
        self.repository_reader = repository_reader
        self.document_chunker = document_chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.local_file_reader = local_file_reader
        self.workflow = self._build_workflow()

    def _clone_repository(self, state: RAGState) -> RAGState:
        """Clone the repository and check for existing documents."""
        print("\n=== Step 1: Cloning Repository & Checking Existing Data ===")
        try:
            # Check for existing documents first
            if state.get("skip_existing_documents") and not state.get("force_reprocess"):
                print("Checking vector store for existing documents...")
                existing_paths = self.vector_store.get_existing_file_paths()
                state["existing_file_paths"] = existing_paths
                if existing_paths:
                    print(f"Found {len(existing_paths)} existing documents in vector store")
            else:
                state["existing_file_paths"] = set()

            # Clone repository (will return empty string if no URL provided)
            repo_url = state.get("repository_url", "")
            if repo_url and repo_url.strip():
                repo_path = self.repository_reader.clone_repository(repo_url)
                state["repo_path"] = repo_path
            else:
                print("No repository URL provided - will process local files only")
                state["repo_path"] = ""

            state["status"] = "repository_cloned"
        except Exception as e:
            state["error"] = f"Failed to clone repository: {str(e)}"
            state["status"] = "error"
        return state

    def _extract_documents(self, state: RAGState) -> RAGState:
        """Extract markdown documents from the repository."""
        print("\n=== Step 2: Extracting Markdown Documents ===")
        if state.get("error"):
            return state

        try:
            repo_path = state.get("repo_path", "")
            if repo_path and repo_path.strip():
                documents = self.repository_reader.get_markdown_files(repo_path)
                state["documents"] = documents
                print(f"Extracted {len(documents)} markdown documents from repository")
            else:
                print("No repository cloned - will rely on local files only")
                state["documents"] = []

            state["status"] = "documents_extracted"
        except Exception as e:
            state["error"] = f"Failed to extract documents: {str(e)}"
            state["status"] = "error"
        return state

    def _process_local_files(self, state: RAGState) -> RAGState:
        """Process local files from data directory."""
        print("\n=== Step 3: Processing Local Files (Diagrams, Images, Documents) ===")
        if state.get("error"):
            return state

        # Skip if local file processing is disabled or reader not available
        if not state.get("process_local_files") or not self.local_file_reader:
            print("Skipping local file processing (disabled or not configured)")
            return state

        try:
            local_dir = state.get("local_data_dir")
            if local_dir:
                local_documents = self.local_file_reader.read_directory(local_dir)
                # Append local documents to existing documents
                state["documents"].extend(local_documents)
                print(f"Processed {len(local_documents)} local files")
                print(f"Total documents: {len(state['documents'])}")
            else:
                print("No local data directory specified")
        except Exception as e:
            # Don't fail the entire workflow if local processing fails
            print(f"Warning: Failed to process local files: {str(e)}")

        return state

    def _filter_existing_documents(self, state: RAGState) -> RAGState:
        """Filter out documents that are already in the vector store."""
        print("\n=== Step 4: Checking for Existing Documents ===")
        if state.get("error"):
            return state

        # If force reprocess is enabled, skip filtering
        if state.get("force_reprocess"):
            print("Force reprocess enabled - will process all documents")
            state["skipped_count"] = 0
            state["new_count"] = len(state["documents"])
            return state

        # If skip existing is disabled, process all
        if not state.get("skip_existing_documents"):
            print("Skip existing disabled - will process all documents")
            state["skipped_count"] = 0
            state["new_count"] = len(state["documents"])
            return state

        try:
            # Get existing file paths from vector store
            existing_paths = state.get("existing_file_paths", set())

            if not existing_paths:
                print("No existing documents found in vector store")
                state["skipped_count"] = 0
                state["new_count"] = len(state["documents"])
                return state

            print(f"Found {len(existing_paths)} unique file paths in vector store")

            # Filter documents
            original_count = len(state["documents"])
            new_documents = []

            for doc in state["documents"]:
                if doc.file_path not in existing_paths:
                    new_documents.append(doc)
                else:
                    print(f"  Skipping (already indexed): {doc.file_path}")

            state["documents"] = new_documents
            state["skipped_count"] = original_count - len(new_documents)
            state["new_count"] = len(new_documents)

            print(f"\n📊 Document Status:")
            print(f"  - Total found: {original_count}")
            print(f"  - Already indexed: {state['skipped_count']}")
            print(f"  - New to process: {state['new_count']}")

            if state["new_count"] == 0:
                print("\n✅ All documents are already indexed. Nothing to process!")
                state["status"] = "no_new_documents"

        except Exception as e:
            print(f"Warning: Could not filter existing documents: {str(e)}")
            print("Will process all documents to be safe...")
            state["skipped_count"] = 0
            state["new_count"] = len(state["documents"])

        return state

    def _chunk_documents(self, state: RAGState) -> RAGState:
        """Chunk the documents."""
        print("\n=== Step 5: Chunking Documents ===")
        if state.get("error"):
            return state

        # Skip if no new documents
        if state.get("status") == "no_new_documents":
            print("No new documents to chunk")
            return state

        try:
            chunks = self.document_chunker.chunk_documents(state["documents"])
            state["chunks"] = chunks
            state["status"] = "documents_chunked"
            print(f"Created {len(chunks)} chunks")
        except Exception as e:
            state["error"] = f"Failed to chunk documents: {str(e)}"
            state["status"] = "error"
        return state

    def _create_embeddings(self, state: RAGState) -> RAGState:
        """Create embeddings for chunks."""
        print("\n=== Step 6: Creating Embeddings ===")
        if state.get("error"):
            return state

        # Skip if no new documents
        if state.get("status") == "no_new_documents":
            print("No new documents to embed")
            return state

        try:
            chunks = state["chunks"]
            texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.create_embeddings(texts)

            embedded_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                embedded_chunk = EmbeddedChunk(
                    chunk=chunk,
                    embedding=embedding
                )
                embedded_chunks.append(embedded_chunk)

            state["embedded_chunks"] = embedded_chunks
            state["status"] = "embeddings_created"
            print(f"Created {len(embedded_chunks)} embeddings")
        except Exception as e:
            state["error"] = f"Failed to create embeddings: {str(e)}"
            state["status"] = "error"
        return state

    def _store_embeddings(self, state: RAGState) -> RAGState:
        """Store embeddings in Milvus."""
        print("\n=== Step 7: Storing Embeddings in Milvus ===")
        if state.get("error"):
            return state

        # Skip if no new documents
        if state.get("status") == "no_new_documents":
            print("No new embeddings to store")
            return state

        try:
            # Use initialize_or_load_collection instead of initialize_collection
            # This will preserve existing documents
            self.vector_store.initialize_or_load_collection()
            self.vector_store.insert_embeddings(state["embedded_chunks"])
            state["status"] = "embeddings_stored"
            print("Successfully stored embeddings in Milvus")
        except Exception as e:
            state["error"] = f"Failed to store embeddings: {str(e)}"
            state["status"] = "error"
        return state

    def _cleanup(self, state: RAGState) -> RAGState:
        """Cleanup temporary files."""
        print("\n=== Step 8: Cleanup ===")
        try:
            if state.get("repo_path"):
                self.repository_reader.cleanup(state["repo_path"])
                print("Cleanup completed")
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")

        # Set final status
        if state.get("status") == "no_new_documents":
            state["status"] = "completed_no_changes"
        elif not state.get("error"):
            state["status"] = "completed"
        else:
            state["status"] = "failed"

        return state

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(RAGState)

        # Add nodes
        workflow.add_node("clone_repository", self._clone_repository)
        workflow.add_node("extract_documents", self._extract_documents)
        workflow.add_node("process_local_files", self._process_local_files)
        workflow.add_node("filter_existing_documents", self._filter_existing_documents)
        workflow.add_node("chunk_documents", self._chunk_documents)
        workflow.add_node("create_embeddings", self._create_embeddings)
        workflow.add_node("store_embeddings", self._store_embeddings)
        workflow.add_node("cleanup", self._cleanup)

        # Define the flow
        workflow.set_entry_point("clone_repository")
        workflow.add_edge("clone_repository", "extract_documents")
        workflow.add_edge("extract_documents", "process_local_files")
        workflow.add_edge("process_local_files", "filter_existing_documents")
        workflow.add_edge("filter_existing_documents", "chunk_documents")
        workflow.add_edge("chunk_documents", "create_embeddings")
        workflow.add_edge("create_embeddings", "store_embeddings")
        workflow.add_edge("store_embeddings", "cleanup")
        workflow.add_edge("cleanup", END)

        return workflow.compile()

    def run(
        self,
        repository_url: str,
        local_data_dir: str = "",
        process_local_files: bool = False,
        skip_existing_documents: bool = True,
        force_reprocess: bool = False
    ) -> RAGState:
        """
        Run the RAG workflow.

        Args:
            repository_url: URL of the repository to process
            local_data_dir: Path to local data directory
            process_local_files: Whether to process local files
            skip_existing_documents: Skip documents already in vector store
            force_reprocess: Force reprocessing of all documents (overrides skip_existing)

        Returns:
            Final state of the workflow
        """
        initial_state: RAGState = {
            "repository_url": repository_url,
            "repo_path": "",
            "local_data_dir": local_data_dir,
            "process_local_files": process_local_files,
            "skip_existing_documents": skip_existing_documents,
            "force_reprocess": force_reprocess,
            "documents": [],
            "chunks": [],
            "embedded_chunks": [],
            "error": "",
            "status": "initialized",
            "existing_file_paths": set(),
            "skipped_count": 0,
            "new_count": 0
        }

        print(f"\n{'='*60}")
        print(f"Starting RAG Workflow")
        print(f"{'='*60}")
        print(f"Repository: {repository_url}")
        if process_local_files and local_data_dir:
            print(f"Local data directory: {local_data_dir}")
        if force_reprocess:
            print(f"Mode: FORCE REPROCESS (will process all documents)")
        elif skip_existing_documents:
            print(f"Mode: INCREMENTAL (will skip existing documents)")
        else:
            print(f"Mode: FULL REINDEX (will process all documents)")
        print(f"{'='*60}")

        final_state = self.workflow.invoke(initial_state)

        print(f"\n{'='*60}")
        print(f"Workflow Status: {final_state['status']}")
        print(f"{'='*60}")

        if final_state.get("error"):
            print(f"❌ Error: {final_state['error']}")
        elif final_state['status'] == 'completed_no_changes':
            print(f"✅ All documents already indexed - no changes needed!")
            print(f"   - Skipped: {final_state.get('skipped_count', 0)} documents")
            print(f"\n💡 Tip: Use FORCE_REPROCESS=true in .env to reprocess all documents")
        else:
            print(f"✅ Successfully completed!")
            print(f"\n📊 Summary:")
            print(f"   - Total documents found: {final_state.get('skipped_count', 0) + final_state.get('new_count', 0)}")
            print(f"   - Already indexed (skipped): {final_state.get('skipped_count', 0)}")
            print(f"   - Newly processed: {final_state.get('new_count', 0)}")
            print(f"   - Chunks created: {len(final_state['chunks'])}")
            print(f"   - Embeddings stored: {len(final_state['embedded_chunks'])}")

        print(f"{'='*60}\n")

        return final_state
        print(f"{'='*60}\n")

        return final_state

