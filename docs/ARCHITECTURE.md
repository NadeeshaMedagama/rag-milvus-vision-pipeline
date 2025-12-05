# SOLID Principles Implementation
5. **Clarity**: Clear separation of concerns makes code easier to understand
4. **Flexibility**: Easy to swap implementations (e.g., use different vector stores)
3. **Extensibility**: New features can be added without modifying existing code
2. **Maintainability**: Changes are localized to specific classes
1. **Testability**: Easy to mock interfaces for unit testing

## Benefits

```
└────────┘ └────────┘ └────────┘ └──────────────┘
│Reader  │ │Chunker │ │OpenAI  │ │VectorStore   │
│GitHub  │ │Document│ │Azure   │ │Milvus        │
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐
    ▼          ▼          ▼           ▼
    │          │          │           │
└───┬────┘ └───┬────┘ └───┬────┘ └────┬───────────────┘
│Reader  │ │Chunker │ │Service │ │                    │
│IRepo   │ │IDoc    │ │IEmbed  │ │IVectorStore        │
┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────────┐
  ▼          ▼          ▼          ▼
  │          │          │          │
└─┬──────────┬──────────┬──────────┬──────────────────────────┘
│              (Workflow Orchestration)                        │
│                    RAGWorkflow                               │
┌─────────────────────────────────────────────────────────────┐
                     ▼
                     │
└────────────────────┬────────────────────────────────────────┘
│                  (Dependency Assembly)                       │
│                         main.py                              │
┌─────────────────────────────────────────────────────────────┐
```

## Architecture Diagram

- The main application assembles the dependencies and injects them
- Dependencies are injected through the constructor
- `RAGWorkflow` depends on interfaces (`IRepositoryReader`, `IDocumentChunker`, etc.)

High-level modules depend on abstractions, not concrete implementations:

## Dependency Inversion Principle (DIP)

Each interface contains only the methods needed for its specific purpose.

- `IVectorStore`: Methods for vector storage operations
- `IEmbeddingService`: Methods for embedding creation
- `IDocumentChunker`: Methods for chunking operations
- `IRepositoryReader`: Methods for repository operations

Interfaces are small and focused:

## Interface Segregation Principle (ISP)

- You can swap `AzureOpenAIEmbeddingService` with another implementation of `IEmbeddingService`
- The workflow depends on interfaces, not concrete implementations
- All service implementations strictly follow their interface contracts

Any implementation of an interface can be substituted without breaking the application:

## Liskov Substitution Principle (LSP)

- For example, you can add a new embedding service by implementing `IEmbeddingService`
- New implementations can be added without modifying existing code
- All services implement interfaces (abstract base classes)

The system is open for extension but closed for modification:

## Open/Closed Principle (OCP)

- **RAGWorkflow**: Only orchestrates the workflow
- **MilvusVectorStore**: Only handles vector storage operations
- **AzureOpenAIEmbeddingService**: Only handles embedding creation
- **DocumentChunker**: Only handles document chunking
- **GitHubRepositoryReader**: Only handles cloning repositories and reading markdown files

Each class has a single, well-defined responsibility:

## Single Responsibility Principle (SRP)

This project follows SOLID principles to ensure maintainability, scalability, and testability.


