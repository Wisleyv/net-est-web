# Workflow for a Computational System for the Analysis of Simplification Strategies in Intralingual Translation

## Basic Description

### Main function

Compare source texts (ST) with target texts (TT) of an intralingual translation (from Portuguese into Portuguese) to identify simplification strategies employed by translators, and use tags to mark in both ST and TT:

- where the simplificatication occurred

- how it was applied

- which simplifications occurred in each segment

- signal overlapping simplifications - grading by precedence
  
  
  
  allow tags to be altered/inserted by a human-in-the-loop
  
  

The system is to be designed to work under the supervision of a human-in-the-loop as the main linguist who is the validator of the system findings.

The analysis is to be done in the discourse level, taking the paragraph as the analysis unity. Semantical alignment and detection of simplification strategies are to be done with the help a Neural Language Model (paraphrase-multilingual-MiniLM-L12-v2) combined with appropriate Python libraries.

Once simplification strategies are detected and the respective tags are inserted in the TT, the human agent has to be able to insert new tags, edit and delete tags inserted by the system.

Once tags are validated, the system has to be able issue reports that include a side-by-side exhibition of ST and TT, highlighting in both texts where the detected simplification strategies occur and placing superscript tags in the body of the TT. 

The app will run on HuggingFace Spaces (backend) and personal or Vercel like website (frontend)

### Basic Workflow

START

1. User submits ST and TT (simplified with approximately 65% less words than the ST)
   
   - Submission can be typed into text boxes for ST and TT or uploaded (PDF, ODT, DOCX, MD and TXT file types)

2- System preprocesses and validates both ST and TT
   
   - Words count for both texts
   
   - Segmentation for analysis/mapping: phrase is the unity
   
   - TT length reduction index (%)

3- Semantic alignment identifies paragraph correspondences

4- Feature extraction analyses aligned pairs
   
   - Both ST and TT are mapped to locate where simplification strategies were applied
     
     - For this mapping, the phrase (sintagma - in Portuguese) is the default level of placement accuracy: a sentence can accommodate multiple strategies, therefore, tags

5- Classification engine applies tags based on detected strategies
   
   - Overlapping strategies are detected
     
     - A threshold of confidence (65%) determines the insertion of tags
     
     - When overlapping occurs, confidence index determines their classification and positioning 
       
       - Tags with higher confidence index are shown with a visual sign that other tags were detected
         
         - A click on that sign display and allows the human agent to select ony of them to replace the one detected by the system
   
   - 14 tags and their respective descriptions are provided in a table with instructions about two special cases
   
   - Tags placement follows the mapping for detection: the unity is the "phrase" (sintagma)
     
     - Tags are superscript at the beginning of the phrase where a strategy is detected

6- User interface displays results with interactive editing capabilities
   
   - A color code is used to highlight the phrase where a strategy is detected
     
     - Both ST and TT are "mapped" with this color code to visually show the correspondence between ST and TT
     
     - Each strategy has a unique color
     
     - When the human agent changes a tag, the highlighting color changes accordingly

7- User instruct the system to issue reports that contain
   
   - both ST and TT side-by-side displaying the mapped texts with their tags and color codes
   
   - a list of strategies found and their respective number of occurrences
   
   - a bar graph displaying the statistics of:
     
     - TT length reduction indice
     
     - Identified strategies and their frequencies

8- User feedback is captured for future improvements and model training

9- 

END


























