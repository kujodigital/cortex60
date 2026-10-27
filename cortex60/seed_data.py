"""Curated multi-disciplinary knowledge base for Block 1 (6 Domains) and Block 3 (Mental Models)."""

INSIGHT_CONCEPTS = [
    {
        "id": "insight_hist_geo_01",
        "domain": "History/Geography",
        "title": "Thalassocratic Chokepoints: From the Strait of Malacca (1511) to Modern Silicon Geopolitics",
        "reading_target_minutes": 10,
        "recall_target_minutes": 5,
        "word_count": 440,
        "cross_disciplines": ["Maritime Geography", "Imperial History", "Semiconductor Supply Chains"],
        "content_html": """
            <p><strong>1. The Geographic Imperative of Maritime Funnels:</strong> Throughout recorded history, global trade has been governed by physical hydrography. Fewer than ten maritime passages—chief among them the <em>Strait of Malacca</em> (between the Malay Peninsula and Sumatra), the <em>Bab el-Mandeb</em>, the <em>Strait of Hormuz</em>, and the <em>Turkish Straits</em>—act as high-pressure valves for planetary commerce. At its narrowest point in the Phillips Channel near Singapore, the Strait of Malacca constricts to just <strong>1.5 nautical miles (2.8 km)</strong>, yet carries roughly 25% of all traded goods and 80% of Northeast Asia's crude oil imports.</p>
            <p><strong>2. Primary Historical Turning Point (1511 CE):</strong> Recognizing that whoever controlled these narrows could tax the spice trade without conquering continental interiors, Portuguese strategist <strong>Afonso de Albuquerque</strong> captured the Sultanate of Malacca in <strong>August 1511</strong>, after previously seizing Goa (1510) and later Hormuz (1515). Unlike land empires (such as the Ming Dynasty or Mughal Empire) that derived revenue from agrarian taxation, Portugal constructed a <em>cartaz</em> (licensing) system—a network of fortified naval nodes extracting rent from oceanic transit. The Dutch East India Company (VOC), headquartered in Batavia (modern <strong>Jakarta</strong>, capital of Indonesia), seized Malacca from the Portuguese in <strong>1641</strong>, shifting capital allocation toward joint-stock maritime monopolies.</p>
            <p><strong>3. Modern Economic & Technological Consequence:</strong> In the 21st century, the exact hydrographic constraints that dictated 16th-century spice prices now govern the global semiconductor and energy architecture. Ultra-pure quartz, neon, EUV lithography subsystems, and LNG tankers bound for fabrication plants near <strong>Taipei</strong> and <strong>Seoul</strong> must transit the Luzon and Malacca corridors. A 14-day closure of the Strait of Malacca forces vessels to detour through the <em>Lombok</em> or <em>Sunda</em> Straits, adding ~1,000 nautical miles, spiking global freight spot rates by 35–60%, and triggering working-capital liquidity crunches in just-in-time electronics manufacturing.</p>
            <p><strong>4. Analytical Fallacy Case for Evaluation:</strong> Critics of maritime infrastructure investment frequently argue: <em>"Because air freight carries high-value-to-weight microchips and digital data travels over fiber-optic cables, maritime chokepoints are obsolete relics of the sail era; investing in port redundancy is wasted capital."</em> (Examine the structural flaw in this argument during active recall.)</p>
        """,
        "questions": [
            {
                "tier": "Foundational",
                "question": "In what year did Portuguese strategist Afonso de Albuquerque capture the Sultanate of Malacca, and what modern capital city corresponds to the VOC's headquarters of Batavia?",
                "options": [
                    "1511 CE; Jakarta (Indonesia)",
                    "1641 CE; Kuala Lumpur (Malaysia)",
                    "1498 CE; Manila (Philippines)",
                    "1588 CE; Colombo (Sri Lanka)"
                ],
                "correct_index": 0,
                "explanation": "Albuquerque captured Malacca in August 1511 (the Dutch VOC captured it in 1641), and Batavia is modern-day Jakarta, capital of Indonesia."
            },
            {
                "tier": "Intermediate",
                "question": "Identify the primary logical fallacy in the passage's paragraph 4 argument ('Because air freight carries microchips... maritime chokepoints are obsolete'):",
                "options": [
                    "Composition / Omission of Base-Layer Inputs: Ignoring that the energy (LNG/oil) and bulk chemical precursors required to fabricate chips and power data centers still move almost exclusively by sea.",
                    "Ad Hominem: Attacking naval historians rather than addressing shipping tonnage.",
                    "Sunk Cost Fallacy: Refusing to abandon existing port facilities despite declining usage.",
                    "Post Hoc Ergo Propter Hoc: Assuming fiber-optic cables caused the rise of air freight."
                ],
                "correct_index": 0,
                "explanation": "While finished wafers can fly by air, the electricity generation (LNG/crude) and bulk chemical precursors for fabs depend on maritime chokepoints."
            },
            {
                "tier": "Advanced",
                "question": "Cross-Disciplinary Synthesis: Using a structural systems lens, how does the 16th-century Portuguese 'cartaz' naval node strategy parallel modern semiconductor supply-chain bottlenecks?",
                "options": [
                    "Both rely on controlling irreproducible, high-capital chokepoints (narrow straits vs. EUV lithography/advanced packaging nodes) rather than owning the entire downstream commodity territory.",
                    "Both depend on maximizing agricultural land area and high-headcount labor forces to lower marginal unit costs.",
                    "Both eliminate geopolitical risk by decentralizing production equally across every sovereign nation.",
                    "Both prioritize low-margin bulk commodities over high-barrier technological standards."
                ],
                "correct_index": 0,
                "explanation": "Just as Portugal controlled the Malacca/Hormuz funnels without conquering continental Asia, modern tech dominance rests on controlling non-substitutable chokepoint nodes (like ASML EUV and TSMC leading-edge nodes)."
            }
        ]
    },
    {
        "id": "insight_sci_tech_02",
        "domain": "Science/Tech",
        "title": "Thermodynamics of Information: Landauer's Principle, Entropy & the Energy Wall of AI Compute",
        "reading_target_minutes": 10,
        "recall_target_minutes": 5,
        "word_count": 430,
        "cross_disciplines": ["Statistical Mechanics", "Computer Architecture", "Macro-Energy Economics"],
        "content_html": """
            <p><strong>1. Information Is Physical:</strong> In <strong>1961</strong>, IBM physicist <strong>Rolf Landauer</strong> resolved the century-old <em>Maxwell's Demon</em> paradox (first proposed by James Clerk Maxwell in <strong>1867</strong> in Edinburgh/Cambridge) by proving that information manipulation is bound by the Second Law of Thermodynamics. Specifically, <strong>Landauer's Principle</strong> states that any logically <em>irreversible</em> computation—such as erasing 1 bit of information (resetting a register to zero regardless of its prior state)—must dissipate a minimum heat energy of <code>k_B · T · ln(2)</code> into the environment, where <code>k_B</code> is the Boltzmann constant and <code>T</code> is absolute temperature.</p>
            <p><strong>2. Quantitative Reality vs. Theoretical Floor:</strong> At room temperature (300 K), the Landauer limit is approximately <strong>2.87 × 10⁻²¹ Joules</strong> per erased bit. Modern 3nm CMOS transistors operate roughly 10,000 to 100,000 times above this thermodynamic floor due to capacitive charging and interconnect resistance—meaning over 90% of energy in modern AI accelerators is consumed not by the arithmetic logic units (ALUs) themselves, but by shuttling electrons across copper interconnects between HBM memory and compute dies (the <em>Von Neumann bottleneck</em>).</p>
            <p><strong>3. Reversible Computing & Photonic Interconnects:</strong> Because logically <em>reversible</em> gates (such as the <strong>Toffoli gate</strong> and <strong>Fredkin gate</strong>, where inputs can always be uniquely reconstructed from outputs) do not destroy information entropy, they theoretically bypass the Landauer heat dissipation floor. In parallel, silicon photonics replaces resistive copper traces with optical waveguides, shifting data movement from electron capacitance to phase-modulated photons.</p>
            <p><strong>4. Analytical Fallacy Case for Evaluation:</strong> A venture report claims: <em>"Every time transistor density doubles under Moore's Law, the total electricity required by global data centers automatically drops by 50%, so power grid expansion is unnecessary."</em></p>
        """,
        "questions": [
            {
                "tier": "Foundational",
                "question": "In what year did Rolf Landauer formulate Landauer's Principle, and what is the exact thermodynamic formula for the minimum energy dissipated when erasing one bit of information?",
                "options": [
                    "1961; E = k_B · T · ln(2)",
                    "1867; E = m · c²",
                    "1948; E = h · f / 2",
                    "1975; E = ½ · C · V²"
                ],
                "correct_index": 0,
                "explanation": "Rolf Landauer published the principle in 1961, establishing the minimum energy dissipation per erased bit as k_B · T · ln(2)."
            },
            {
                "tier": "Intermediate",
                "question": "Which economic/logical error invalidates the paragraph 4 claim that doubling transistor efficiency halves total global data center electricity demand?",
                "options": [
                    "Neglecting Jevons Paradox (Rebound Effect): As the energy cost per FLOP falls, elastic demand for frontier AI training and inference scales exponentially faster than per-unit efficiency gains.",
                    "Survivorship Bias: Only measuring data centers that survived grid outages.",
                    "Appeal to Authority: Citing Gordon Moore without verifying lithography wavelengths.",
                    "Circular Reasoning: Defining efficiency as reduced power consumption."
                ],
                "correct_index": 0,
                "explanation": "First observed by William Stanley Jevons in 1865 with coal steam engines, Jevons Paradox demonstrates that increasing the efficiency of a resource lowers its effective price, driving higher aggregate consumption."
            },
            {
                "tier": "Advanced",
                "question": "Cross-Disciplinary Synthesis: Why do modern AI hardware architects focus on co-packaged optics and in-memory compute rather than solely shrinking CMOS gate lengths?",
                "options": [
                    "Because electron transport across copper interconnects (the Von Neumann memory wall) dominates thermal dissipation far more than transistor switching alone, making sovereign grid capacity and cooling the binding macro-economic constraint.",
                    "Because Landauer's limit only applies to optical fibers and not to silicon transistors.",
                    "Because reversible Toffoli gates are already deployed in all consumer smartphones.",
                    "Because copper interconnects violate the First Law of Thermodynamics."
                ],
                "correct_index": 0,
                "explanation": "Moving data across resistive interconnects accounts for the vast majority of heat and power draw in AI clusters, directly linking sub-nanometer physics to macro-level utility grid bottlenecks."
            }
        ]
    },
    {
        "id": "insight_pol_econ_03",
        "domain": "Politics/Economics",
        "title": "The Triffin Dilemma: Bretton Woods (1944), Reserve Currency Hegemony & Industrial Hollow-Out",
        "reading_target_minutes": 10,
        "recall_target_minutes": 5,
        "word_count": 420,
        "cross_disciplines": ["Monetary History", "International Political Economy", "Trade Balance Mechanics"],
        "content_html": """
            <p><strong>1. The Structural Paradox of Reserve Issuers:</strong> In <strong>1959–1960</strong>, Belgian-American economist <strong>Robert Triffin</strong> testified before the U.S. Congress and exposed a fatal structural contradiction at the heart of the <strong>1944 Bretton Woods</strong> monetary order (negotiated in New Hampshire by John Maynard Keynes and Harry Dexter White, with key European central banking clearing later centered in <strong>Basel</strong>, Switzerland). <strong>The Triffin Dilemma</strong> states that when a single nation's domestic currency also serves as the global reserve currency, its national monetary policy goals inevitably collide with global liquidity requirements.</p>
            <p><strong>2. The Mechanics of the Trap:</strong> To supply the expanding world economy with sufficient reserve liquidity for cross-border trade settlement, the reserve-issuing nation <em>must</em> run persistent current-account / balance-of-payments deficits, exporting its currency abroad. However, running perpetual deficits erodes foreign creditors' confidence in the currency's hard backing (which culminated in President Richard Nixon closing the gold window in <strong>August 1971</strong>) and systematically overvalues the domestic currency relative to export-surplus manufacturing peers.</p>
            <p><strong>3. Second-Order Domestic Consequence:</strong> Because global central banksrecycle trade surpluses into the reserve issuer's sovereign bonds (e.g., U.S. Treasuries), the reserve issuer enjoys artificially suppressed borrowing costs ("exorbitant privilege," coined by Valéry Giscard d'Estaing in <strong>Paris</strong>). Yet the flip side of a persistent capital-account surplus is a structural trade deficit that prices domestic tradable manufacturing out of global markets.</p>
            <p><strong>4. Analytical Fallacy Case for Evaluation:</strong> A commentator argues: <em>"A country can simultaneously maintain a 100% closed capital account, run massive trade surpluses every year, and still have its currency make up 80% of foreign central bank liquid reserves."</em></p>
        """,
        "questions": [
            {
                "tier": "Foundational",
                "question": "In what year was the Bretton Woods agreement negotiated, in what year did Nixon close the gold convertibility window, and which Swiss city hosts the Bank for International Settlements (BIS)?",
                "options": [
                    "1944 (Bretton Woods), 1971 (Nixon Shock), Basel (Switzerland)",
                    "1919 (Bretton Woods), 1989 (Nixon Shock), Geneva (Switzerland)",
                    "1959 (Bretton Woods), 1979 (Nixon Shock), Bern (Switzerland)",
                    "1945 (Bretton Woods), 2008 (Nixon Shock), Zurich (Switzerland)"
                ],
                "correct_index": 0,
                "explanation": "Bretton Woods was signed in July 1944, Nixon suspended gold convertibility in August 1971, and the BIS is headquartered in Basel."
            },
            {
                "tier": "Intermediate",
                "question": "Why is the paragraph 4 claim ('run massive trade surpluses + closed capital account + 80% global reserve share') a logical contradiction under balance-of-payments accounting?",
                "options": [
                    "Accounting Identity Violation: For rest-of-world central banks to accumulate net liquid reserves of Currency X, the issuer of X must supply net currency/assets abroad via current-account deficits or open capital outflows.",
                    "Gambler's Fallacy: Assuming past currency appreciation guarantees future depreciation.",
                    "Straw Man Fallacy: Misrepresenting the gold standard.",
                    "False Equivalency: Comparing inflation rates to unemployment rates."
                ],
                "correct_index": 0,
                "explanation": "By the Balance of Payments identity (Current Account + Capital/Financial Account = 0), foreign accumulation of a reserve currency requires the issuer to be a net supplier of safe financial assets and liquidity."
            },
            {
                "tier": "Advanced",
                "question": "Cross-Disciplinary Synthesis: How does the Triffin Dilemma connect 20th-century monetary architecture to 21st-century industrial re-shoring friction?",
                "options": [
                    "Foreign demand for reserve-currency debt keeps the reserve currency structurally stronger than trade-balance equilibrium, acting as an implicit tax on domestic export manufacturing while subsidizing financialization.",
                    "Reserve status forces the issuing country to ban all foreign investment in its sovereign bond market.",
                    "The Triffin Dilemma only applies when currencies are backed by silver coins.",
                    "Re-shoring factories automatically eliminates the need for international trade settlement."
                ],
                "correct_index": 0,
                "explanation": "Inelastic foreign demand for reserve assets strengthens the currency independently of trade fundamentals, creating headwinds for domestic tradable goods production."
            }
        ]
    },
    {
        "id": "insight_phil_lit_04",
        "domain": "Philosophy/Literature",
        "title": "Formal Limits of Reason: Gödel's Incompleteness (1931), Borges' Babel & Algorithmic Alignment",
        "reading_target_minutes": 10,
        "recall_target_minutes": 5,
        "word_count": 415,
        "cross_disciplines": ["Mathematical Logic", "Metaphysical Literature", "AI Epistemology"],
        "content_html": """
            <p><strong>1. The Collapse of Hilbert's Program:</strong> At the turn of the 20th century, mathematician David Hilbert challenged the world to prove that mathematics was both <em>complete</em> (every true statement can be proven) and <em>consistent</em> (no contradictions can be derived). In <strong>1931</strong>, working in <strong>Vienna</strong> (capital of Austria), 25-year-old logician <strong>Kurt Gödel</strong> published his First and Second Incompleteness Theorems, shattering formalist absolutism. Using <em>Gödel numbering</em> to encode meta-mathematical statements into arithmetic, Gödel constructed a self-referential formula equivalent to: <em>"This statement cannot be proven within axiom system S."</em></p>
            <p><strong>2. The Two Inescapable Horns:</strong> If the statement is false, then it is provable—meaning system S proves a falsehood and is <strong>inconsistent</strong>. If the statement is true, then it cannot be proven within S—meaning S is <strong>incomplete</strong>. Furthermore, Gödel's Second Theorem proved that no sufficiently powerful consistent formal system can prove its own consistency from within.</p>
            <p><strong>3. Literary Isomorphism in Jorge Luis Borges:</strong> Ten years later, in <strong>1941</strong> in <strong>Buenos Aires</strong> (capital of Argentina), writer <strong>Jorge Luis Borges</strong> published <em>The Library of Babel</em>—depicting an infinite hexagonal universe containing every possible 410-page permutation of orthographic symbols. Because the library is "total" (complete), it contains every true prophecy alongside millions of subtle falsehoods and contradictions, rendering pure syntactic completeness epistemically useless without an external filter for meaning.</p>
            <p><strong>4. Analytical Fallacy Case for Evaluation:</strong> A compliance architect claims: <em>"By writing a 10,000-rule formal smart contract constitution, we have created a self-contained rule system that is 100% complete for all possible economic disputes and internally proves its own unbreakability."</em></p>
        """,
        "questions": [
            {
                "tier": "Foundational",
                "question": "In what year and city did Kurt Gödel publish his Incompleteness Theorems, and in what year and capital city did Jorge Luis Borges publish 'The Library of Babel'?",
                "options": [
                    "1931 in Vienna (Austria); 1941 in Buenos Aires (Argentina)",
                    "1915 in Berlin (Germany); 1955 in Madrid (Spain)",
                    "1936 in London (UK); 1949 in Santiago (Chile)",
                    "1921 in Prague (Czechia); 1961 in Lisbon (Portugal)"
                ],
                "correct_index": 0,
                "explanation": "Gödel published his theorems in 1931 while in Vienna; Borges published 'The Library of Babel' in 1941 in Buenos Aires."
            },
            {
                "tier": "Intermediate",
                "question": "What formal logical fallacy / impossibility does the paragraph 4 compliance architect commit?",
                "options": [
                    "Violation of Gödelian Meta-System Limits: Assuming a non-trivial formal system can simultaneously be complete for all expressive states and self-verify its own consistency without an external meta-adjudicator.",
                    "Texas Sharpshooter Fallacy: Cherry-picking favorable data clusters after the fact.",
                    "Bandwagon Fallacy: Assuming a smart contract is secure because it is popular.",
                    "Tu Quoque: Deflecting criticism onto legacy courts."
                ],
                "correct_index": 0,
                "explanation": "Any sufficiently expressive formal rule system cannot be both complete and consistent, nor can it prove its own consistency without appealing to an external meta-layer."
            },
            {
                "tier": "Advanced",
                "question": "Cross-Disciplinary Synthesis: How do Gödel's Incompleteness and Borges' Library of Babel inform modern AI alignment and legal contract design?",
                "options": [
                    "Purely syntactic rule-sets or ungrounded token generators inevitably encounter undecidable edge cases (specification gaming / reward hacking), requiring external empirical grounding and human constitutional oversight.",
                    "They prove that adding more random text to a training corpus automatically eliminates hallucinations.",
                    "They show that mathematics should be replaced with literary fiction in central banking.",
                    "They prove that computers cannot perform basic addition."
                ],
                "correct_index": 0,
                "explanation": "Both works demonstrate that closed syntactic systems cannot self-ground truth or resolve every edge case without an external semantic/empirical reference frame."
            }
        ]
    },
    {
        "id": "insight_arts_cult_05",
        "domain": "Arts/Culture",
        "title": "Architectural Acoustics & Polyphony: Sabine's Reverberation Law, Venice (1562) & Sensory Economics",
        "reading_target_minutes": 10,
        "recall_target_minutes": 5,
        "word_count": 410,
        "cross_disciplines": ["Acoustic Physics", "Renaissance Musicology", "Experience Economy Design"],
        "content_html": """
            <p><strong>1. Architecture Shapes Artistic Form:</strong> Art history is frequently taught as an isolated progression of personal genius, yet physical architecture acts as the evolutionary selection environment for musical structure. In the 16th century, <strong>St. Mark's Basilica</strong> in <strong>Venice</strong> featured an unusual Byzantine cross-plan with opposing elevated choir lofts and a long reverberation time (~4.5 seconds). Because rapid monophonic chants blurred into muddy echoes across that distance, composer <strong>Adrian Willaert</strong> and later <strong>Giovanni Gabrieli</strong> (appointed in <strong>1585</strong>) pioneered <em>cori spezzati</em> (spatially separated polychoral antiphony)—turning architectural delay into stereo harmonic interplay.</p>
            <p><strong>2. Quantitative Physics of Reverberation (1898):</strong> Over three centuries later, Harvard physicist <strong>Wallace Clement Sabine</strong> formalized architectural acoustics into a precise physical law: <code>RT60 = 0.161 · V / A</code>, where <code>RT60</code> is the time (in seconds) required for sound energy to decay by 60 decibels, <code>V</code> is room volume (m³), and <code>A</code> is total effective absorption area (sabins).</p>
            <p><strong>3. Modern Cognitive & Commercial Application:</strong> High <code>RT60</code> (>2.0s) enriches slow harmonic sustain (organ music, cathedrals) but destroys speech consonant intelligibility (which resides in the 2–4 kHz band). Conversely, modern workplace and trading-floor architecture often suffers from reflective glass-and-concrete surfaces that raise ambient noise by 8–12 dB, elevating cortisol and reducing complex reading comprehension velocity by up to 25%.</p>
            <p><strong>4. Analytical Fallacy Case for Evaluation:</strong> An interior architect states: <em>"Because symphony halls with a 2.2-second reverberation time are rated highest for acoustic prestige, designing a high-frequency financial trading & legal research office with a 2.2-second reverberation time will maximize worker productivity."</em></p>
        """,
        "questions": [
            {
                "tier": "Foundational",
                "question": "In Sabine's reverberation formula (RT60 = 0.161 · V / A), what does RT60 measure, and which Venetian basilica gave rise to Gabrieli's polychoral 'cori spezzati' style?",
                "options": [
                    "Time for sound to decay by 60 dB; St. Mark's Basilica in Venice",
                    "Frequency of a 60 Hz wave; St. Peter's Basilica in Rome",
                    "Speed of sound at 60°F; Notre-Dame in Paris",
                    "Decibel level at 60 meters; Hagia Sophia in Istanbul"
                ],
                "correct_index": 0,
                "explanation": "RT60 is the time for sound pressure level to decay by 60 decibels, and St. Mark's Basilica in Venice catalyzed the Venetian polychoral style."
            },
            {
                "tier": "Intermediate",
                "question": "Identify the logical fallacy in the paragraph 4 architect's recommendation to use a 2.2s symphony hall RT60 for a speech/research office:",
                "options": [
                    "False Equivalence / Context Blindness: Equating optimal acoustic parameters for sustained symphonic blending with optimal parameters for high-consonant speech intelligibility and cognitive focus (<0.6s RT60).",
                    "Slippery Slope: Arguing that echo leads to building collapse.",
                    "No True Scotsman: Redefining what counts as a symphony.",
                    "Begging the Question: Assuming glass is cheaper than acoustic panels."
                ],
                "correct_index": 0,
                "explanation": "Symphonic music benefits from ~2.0s harmonic blending, whereas speech intelligibility and deep cognitive work require rapid consonant decay (<0.6s) to prevent auditory masking."
            },
            {
                "tier": "Advanced",
                "question": "Cross-Disciplinary Synthesis: How does the co-evolution of Venetian architecture and polychoral music illustrate media-environment determinism in modern digital platforms?",
                "options": [
                    "Just as spatial reverberation times selected for specific musical tempos and harmonies, algorithmic feed latency and format constraints actively select for specific cognitive styles and economic behaviors.",
                    "Digital platforms have no structural constraints on human attention.",
                    "Renaissance composers ignored room acoustics when writing scores.",
                    "Acoustic physics only applies to 16th-century Italy."
                ],
                "correct_index": 0,
                "explanation": "The physical or digital medium acts as a selective filter: architectural acoustics shaped musical syntax just as information-channel latency shapes modern discourse and market microstructure."
            }
        ]
    },
    {
        "id": "insight_fin_health_06",
        "domain": "Finance/Health",
        "title": "Antifragile Bio-Energetics: Hormesis, PGC-1α Mitochondrial Biogenesis & Tail-Risk Convexity",
        "reading_target_minutes": 10,
        "recall_target_minutes": 5,
        "word_count": 435,
        "cross_disciplines": ["Cellular Bioenergetics", "Quantitative Risk Management", "Neurobiology"],
        "content_html": """
            <p><strong>1. The Mathematical Isomorphism of Stressors:</strong> Both biological organisms and financial portfolios fail when optimized for zero variance. In quantitative finance, a portfolio with <em>negative convexity</em> (short volatility) earns small, steady returns in calm regimes but suffers catastrophic ruin during a 3-sigma tail event. Conversely, <em>positive convexity</em> (antifragility) uses bounded, acute stressors to trigger disproportionate upside adaptation.</p>
            <p><strong>2. Cellular Hormesis & PGC-1α Activation:</strong> At the cellular level, chronic unremitting stress (sustained hyperglycemia, sleep deprivation, chronic cortisol) degrades telomeres and hippocampal synapses. However, acute, pulsed energy demand—such as Zone 2 / VO₂-max aerobic intervals or transient caloric depletion—increases the intracellular <strong>AMP:ATP ratio</strong>. This activates <strong>AMPK</strong> and the master transcriptional coactivator <strong>PGC-1α</strong> (discovered in the late <strong>1990s</strong> in Boston), driving <em>mitochondrial biogenesis</em>, clearing damaged organelles via mitophagy, and upregulating <strong>BDNF</strong> (Brain-Derived Neurotrophic Factor) in the hippocampus.</p>
            <p><strong>3. The Kelly Criterion & Recovery Reserves:</strong> In <strong>1956</strong>, Bell Labs researcher <strong>John Larry Kelly Jr.</strong> derived the optimal capital sizing formula for repeated compounding bets. Over-betting beyond the Kelly threshold guarantees eventual ruin even with a positive expected value. Biologically, training load without matching parasympathetic recovery (7–8 hours of slow-wave/REM sleep and omega-3 DHA membrane synthesis) violates the physiological Kelly limit, converting hormetic gain into systemic inflammation.</p>
            <p><strong>4. Analytical Fallacy Case for Evaluation:</strong> A biohacker claims: <em>"Because a 45-minute high-intensity interval session increases BDNF and mitochondrial signalling by 30%, exercising at maximum intensity for 9 hours straight every day with 4 hours of sleep will increase BDNF by 360%."</em></p>
        """,
        "questions": [
            {
                "tier": "Foundational",
                "question": "Which master transcriptional coactivator drives mitochondrial biogenesis in response to an elevated AMP:ATP ratio, and in what year did John Kelly publish the Kelly Criterion?",
                "options": [
                    "PGC-1α; 1956",
                    "Hemoglobin A1c; 1929",
                    "Amyloid-beta; 1987",
                    "Myosin II; 1973"
                ],
                "correct_index": 0,
                "explanation": "PGC-1α is the master regulator of mitochondrial biogenesis, and John L. Kelly Jr. published his information-theoretic bet-sizing paper at Bell Labs in 1956."
            },
            {
                "tier": "Intermediate",
                "question": "What non-linear biological and mathematical error invalidates the paragraph 4 biohacker's linear extrapolation ('45 mins = +30%, therefore 9 hours = +360%')?",
                "options": [
                    "Linear Extrapolation of a Biphasic (Inverted-U) Hormetic Dose-Response Curve: Hormesis exhibits positive convexity only within bounded acute doses followed by recovery; excessive duration flips the sign into catabolic ruin.",
                    "Sunk Cost Fallacy: Refusing to sell gym equipment.",
                    "Ad Populum: Following popular fitness trends.",
                    "Survivorship Bias: Only studying marathon winners."
                ],
                "correct_index": 0,
                "explanation": "Biological hormesis follows an inverted-U (biphasic) curve: acute stress + recovery yields adaptation, whereas unrecovered chronic stress causes cellular breakdown."
            },
            {
                "tier": "Advanced",
                "question": "Cross-Disciplinary Synthesis: How does the Kelly Criterion in portfolio management map onto biological neurogenesis and training recovery?",
                "options": [
                    "Both require maintaining an unencumbered reserve buffer (cash liquidity in finance; sleep/nutritional recovery in biology) so that acute volatility/stress compounds long-term capacity rather than triggering irreversible drawdown.",
                    "Both recommend maximizing leverage to 100% on every single cycle with zero downtime.",
                    "Both prove that avoiding all volatility and physical exertion maximizes long-term growth.",
                    "Both operate linearly regardless of variance."
                ],
                "correct_index": 0,
                "explanation": "Compounding in both capital markets and neurobiology requires pairing bounded stressors with sufficient recovery capacity to prevent ruin."
            }
        ]
    }
]

MENTAL_MODELS = [
    {
        "id": "model_first_principles",
        "name": "First Principles Decomposition",
        "category": "Axiomatic Reasoning & Deconstruction",
        "summary": "Instead of reasoning by analogy ('copying what others do with slight tweaks'), break a complex system down into its fundamental, undeniable physical or economic truths and reconstruct a solution from the ground up.",
        "steps": [
            "1. Surface & list every prevailing industry assumption or 'rule of thumb'.",
            "2. Interrogate each assumption down to physical, mathematical, or material cost floors.",
            "3. Re-architect the solution directly from the verified base constraints."
        ],
        "case_study": {
            "title": "Case Study: Sovereign Grid Storage & Battery Pack Cost Floor",
            "scenario": "You are advising an industrial consortium in 2026 evaluating grid-scale energy storage. Incumbent suppliers quote $180/kWh and claim prices can never drop below $150/kWh because 'historic learning curves in utility procurement only decline 3% per year.' Meanwhile, raw spot commodity prices on the London Metal Exchange for the constituent lithium, nickel, graphite, aluminum, and electrolyte solvents required per kWh sum to just $28/kWh.",
            "fallacy_question": "What cognitive trap are the incumbent suppliers relying on when claiming prices can never drop below $150/kWh?",
            "fallacy_options": [
                "Reasoning by Analogy / Historical Anchoring: Confusing legacy supply-chain markups and organizational inertia with physical material cost floors.",
                "Gambler's Fallacy: Assuming metal prices move randomly.",
                "Confirmation Bias: Ignoring that electricity cannot be stored.",
                "Hindsight Bias: Claiming they predicted battery demand in 1990."
            ],
            "fallacy_correct": 0,
            "application_question": "Applying First Principles Decomposition, what is the highest-leverage executive action for the consortium?",
            "application_options": [
                "Decompose the $152/kWh gap between the $28 commodity floor and $180 quote into specific manufacturing steps (electrode coating, dry-room curing, pack assembly) and redesign the highest-friction fabrication step.",
                "Accept the $180/kWh quote and lobby for a 5% tax credit to bring it to $171/kWh.",
                "Abandon grid storage entirely because historic trends are slow.",
                "Switch to purchasing smaller retail consumer batteries at $300/kWh."
            ],
            "application_correct": 0,
            "synthesis_prompt": "Connect this First Principles material-floor analysis to a historical precedent (e.g., the Bessemer steel process in 1856 or Venice's Arsenal standardized shipbuilding) and explain the modern economic consequence for capital allocation.",
            "synthesis_keywords": ["cost", "material", "process", "standard", "scale", "bottleneck", "capital", "margin", "floor", "production"]
        }
    },
    {
        "id": "model_second_order",
        "name": "Second-Order Thinking ('And Then What?')",
        "category": "Systems Dynamics & Cascading Consequences",
        "summary": "First-order thinking only evaluates the immediate, obvious result of an action. Second- and third-order thinking traces the feedback loops, behavioral adaptations of other actors, and delayed equilibrium shifts over 1, 5, and 10 years.",
        "steps": [
            "1. Map the immediate First-Order effect of a policy or engineering decision.",
            "2. Ask 'And then what?' to model how incentives change for rational participants.",
            "3. Evaluate whether the Second/Third-Order equilibrium reverses the First-Order gain."
        ],
        "case_study": {
            "title": "Case Study: The Cobra Effect & Algorithmic Export Controls",
            "scenario": "In colonial Delhi, authorities offered a cash bounty for every dead cobra skin to reduce the venomous snake population (First-Order goal). Entrepreneurial citizens responded by breeding cobras in farms for the bounty; when authorities canceled the bounty, breeders released the worthless cobras, multiplying the wild population. Today, a policymaker proposes a rigid single-threshold FLOP cap on exported compute chips without regulating cloud rental APIs or chiplet interconnect density.",
            "fallacy_question": "Which structural error characterizes pure First-Order policymaking in both colonial Delhi and naive single-metric hardware caps?",
            "fallacy_options": [
                "Static Agent Assumption (Goodhart's Law): Treating adaptive economic agents as passive objects rather than modeling how they will optimize around the targeted metric.",
                "Sunk Cost Fallacy: Spending too much money on enforcement.",
                "Ad Hominem: Distrusting hardware engineers.",
                "False Dilemma: Assuming only two chip architectures exist."
            ],
            "fallacy_correct": 0,
            "application_question": "Using Second-Order Thinking, what is the predictable 24-month second-order consequence of a naive single-metric FLOP threshold?",
            "application_options": [
                "Targeted actors accelerate R&D into high-bandwidth interconnect clustering of just-below-threshold chips, algorithmic sparsity, and offshore cloud leasing—eroding the exporter's market revenue while catalyzing indigenous rival architectures.",
                "All global competitors permanently cease researching artificial intelligence.",
                "Hardware engineers forget how to connect multiple processors together.",
                "Global electricity consumption drops to zero."
            ],
            "application_correct": 0,
            "synthesis_prompt": "Synthesize how Second-Order Thinking links historical trade blockades (such as Napoleon's 1806 Continental System spurring European beet-sugar and textile industrialization) to modern technology sanctions.",
            "synthesis_keywords": ["incentive", "substitute", "domestic", "adaptation", "feedback", "supply", "indigenous", "market", "loop", "bypass"]
        }
    },
    {
        "id": "model_inversion",
        "name": "Inversion (Jacobi's 'Invert, Always Invert')",
        "category": "Risk Asymmetry & Via Negativa",
        "summary": "Pioneered by mathematician Carl Gustav Jacob Jacobi ('Man muss immer umkehren') and Stoic premeditatio malorum: instead of asking how to achieve brilliant success, rigorously specify every condition that guarantees failure—and systematically engineer those conditions out of existence.",
        "steps": [
            "1. Define the target objective (e.g., resilient capital compounding or high-reliability software).",
            "2. Invert the question: 'How could I guarantee 100% catastrophic failure of this project in 6 months?'",
            "3. Build hard structural guardrails that make each identified failure mode impossible."
        ],
        "case_study": {
            "title": "Case Study: Pre-Mortem Engineering of a Global Payment Clearing Network",
            "scenario": "A fintech infrastructure team is launching a real-time cross-border settlement engine. The team spends 95% of its planning meetings brainstorming flashy marketing features to grow volume by 10x. You are brought in to conduct an Inversion Pre-Mortem before launch.",
            "fallacy_question": "What cognitive bias causes executive teams to obsess over upside growth features while ignoring tail-risk failure modes?",
            "fallacy_options": [
                "Optimism / Survivorship Bias & Neglect of Ruin Probability: Ignoring that in multiplicative systems, any single zero-factor (insolvency, double-spend bug, key compromise) wipes out all prior compounding.",
                "Anchoring Bias: Focusing too much on initial server costs.",
                "Recency Bias: Over-reacting to yesterday's weather.",
                "Framing Effect: Preferring blue logos over green logos."
            ],
            "fallacy_correct": 0,
            "application_question": "Applying Inversion ('How do we guarantee this settlement network collapses?'), which structural guardrail is most critical before launch?",
            "application_options": [
                "Identify the fatal ruin vectors (non-idempotent double-execution on network retry, single-point HSM key compromise, unhedged FX liquidity gap) and enforce cryptographic idempotency keys and automated circuit breakers.",
                "Increase the marketing budget by 50% to attract more early users.",
                "Remove transaction logging to increase database write speed by 4%.",
                "Delay security audits until after reaching 1 million users."
            ],
            "application_correct": 0,
            "synthesis_prompt": "Explain how Inversion ('avoiding stupidity rather than seeking brilliance') connects military logistics history (e.g., supply line protection in ancient campaigns) to modern financial risk management.",
            "synthesis_keywords": ["ruin", "failure", "downside", "survival", "guardrail", "asymmetry", "compounding", "risk", "buffer", "redundancy"]
        }
    },
    {
        "id": "model_occams_razor",
        "name": "Occam's Razor & Diagnostic Parsimony",
        "category": "Epistemic Filtering & Hypothesis Testing",
        "summary": "Formulated by William of Ockham (c. 1287–1347): 'Entities must not be multiplied beyond necessity.' When multiple hypotheses explain an observed dataset equally well, prioritize testing the hypothesis that requires the fewest unproven assumptions.",
        "steps": [
            "1. List all competing explanations for an anomaly or system failure.",
            "2. Count the number of independent, unverified conditional probabilities each explanation requires.",
            "3. Test and falsify the simplest, highest-base-rate mechanism first before invoking complex conspiracies or exotic bugs."
        ],
        "case_study": {
            "title": "Case Study: Submarine Cable Telemetry Drop & Sovereign Market Panic",
            "scenario": "At 03:14 UTC, packet loss between London and Singapore spikes by 40% for 22 minutes, coinciding with a 1.8% flash dip in Asian equity futures. Hypothesis A claims a coordinated quantum-decryption satellite attack simultaneously targeted both the optical seabed repeaters and the exchange matching engine. Hypothesis B notes that an automated BGP route-announcement misconfiguration during scheduled maintenance at a Tier-1 transit carrier forced traffic onto congested backup links, triggering latency-sensitive algorithmic market makers to widen spreads automatically.",
            "fallacy_question": "Which cognitive error drives observers to prefer Hypothesis A over Hypothesis B?",
            "fallacy_options": [
                "Conjunction Fallacy & Proportionality Bias: Assuming that a dramatic market outcome must be caused by an equally dramatic, multi-layered exotic cause rather than a high-base-rate operational single point of failure.",
                "Base Rate Over-Reliance: Relying too heavily on historical network logs.",
                "Sunk Cost Fallacy: Refusing to upgrade routers.",
                "Gambler's Fallacy: Expecting the market to drop again at 04:14 UTC."
            ],
            "fallacy_correct": 0,
            "application_question": "Using Occam's Razor, how should the incident response commander allocate the first 15 minutes of investigation?",
            "application_options": [
                "Immediately inspect BGP routing tables and transit interface error logs (1 conditional variable with high base-rate frequency) before halting all cryptographic protocols for a theoretical quantum attack.",
                "Shut down the entire exchange for 30 days to rebuild quantum-resistant satellites.",
                "Assume both hypotheses are equally likely (50/50) without checking base rates.",
                "Ignore the packet loss entirely."
            ],
            "application_correct": 0,
            "synthesis_prompt": "Link Occam's Razor in scientific history (e.g., Copernicus/Kepler replacing complex Ptolemaic epicycles with heliocentric elliptical orbits) to modern overfitting in quantitative trading models.",
            "synthesis_keywords": ["parameters", "overfitting", "assumptions", "noise", "simpler", "generalize", "epicycles", "base rate", "variables", "signal"]
        }
    }
]
