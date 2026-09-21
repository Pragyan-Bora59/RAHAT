# Smart India Hackathon 2026 - Presentation Visuals

This document contains visual representations (diagrams and flowcharts) of the provided presentation slides. 

## 1. Feasibility Analysis

This diagram illustrates the technical and scope-related feasibility of the idea.

```mermaid
flowchart TD
    classDef main fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px;
    classDef sub fill:#c5cae9,stroke:#303f9f,stroke-width:1px;
    classDef detail fill:#fafafa,stroke:#9e9e9e,stroke-width:1px;
    
    F["✅ Feasibility Analysis"]:::main
    
    F --> F1["🛠️ Technological Base"]:::sub
    F --> F2["🎯 Scope & Achievability"]:::sub
    
    F1 --> F1a["Built entirely on proven GIS & Optimization methods"]:::detail
    F1 --> F1b["Uses readily available ISRO/NRSC satellite datasets"]:::detail
    
    F2 --> F2a["Highly achievable for internal round"]:::detail
    F2 --> F2b["Focuses on targeted, high-risk Dhemaji cluster"]:::detail
    F2 --> F2c["Avoids district-wide scale initially"]:::detail
```

## 2. Challenges and Mitigation Strategies

This flowchart maps the potential risks during an active disaster to the specific strategies implemented to overcome them.

```mermaid
flowchart LR
    classDef challenge fill:#ffcdd2,stroke:#c62828,stroke-width:2px;
    classDef strategy fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px;
    classDef edgeLabel fill:#ffffff,stroke:none;

    subgraph "Challenges & Risks"
        direction TB
        C1["⚠️ Data Gaps<br>Incomplete or missing ground data<br>during active disaster"]:::challenge
        C2["⚠️ Infrastructure Failure<br>Dynamic road accessibility<br>(floods/collapses)"]:::challenge
        C3["⚠️ Resource Limits<br>Severe limitations in relief<br>resources & rescue teams"]:::challenge
    end

    subgraph "Mitigation Strategies"
        direction TB
        S1["🛡️ Separate Data Layers<br>Strictly separate official baseline data from<br>derived scenario data"]:::strategy
        S2["🛡️ Dynamic Adaptability<br>Implement scenario-based<br>route re-optimization"]:::strategy
        S3["🛡️ Smart Prioritization<br>Utilize priority-based optimization<br>algorithms & explainable scoring"]:::strategy
    end

    C1 -->|"Overcome by"| S1
    C2 -->|"Overcome by"| S2
    C3 -->|"Overcome by"| S3
```

## 3. Impact and Benefits

This breakdown highlights the overarching impact on the target audience and categorizes the specific benefits of the solution.

```mermaid
graph TD
    classDef impact fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef benefit fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef detail fill:#fafafa,stroke:#9e9e9e,stroke-width:1px;

    Main["🌟 Solution Impact & Benefits"]:::impact

    Main --> I["🎯 Potential Impact"]:::impact
    Main --> B["💎 Categorized Benefits"]:::benefit

    I --> I1["🔄 Transforms manual, static process into<br>an optimized & adaptive response"]:::detail
    I --> I2["⏱️ Directly impacts stranded populations<br>when every minute matters"]:::detail

    B --> B1["🤝 Social Benefits"]:::benefit
    B --> B2["💰 Economic Benefits"]:::benefit
    B --> B3["⚙️ Operational Benefits"]:::benefit

    B1 -.-> B1a["Prioritizes critical rescue missions"]:::detail
    B1 -.-> B1b["Supports much safer relocation for<br>vulnerable communities"]:::detail

    B2 -.-> B2a["Minimizes resource wastage"]:::detail
    B2 -.-> B2b["Reduces unnecessary deployment of<br>existing government resources"]:::detail

    B3 -.-> B3a["Significantly reduces response time"]:::detail
    B3 -.-> B3b["Ensures safer, feasible routing via<br>dynamic optimization"]:::detail
```
