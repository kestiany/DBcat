# Implementation Plan

- [ ] 1. Create the custom title bar component
  - [x] 1.1 Create the TitleBar class with basic layout and controls


    - Implement title label, window control buttons (minimize, maximize/restore, close)
    - Add application icon to the title bar
    - Style the title bar according to the current theme
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 1.2 Implement window dragging functionality


    - Add mouse event handlers for dragging the window
    - Ensure smooth window movement
    - _Requirements: 1.4_

  - [x] 1.3 Implement window state management


    - Add double-click handler for maximize/restore toggle
    - Ensure maximize button updates its icon based on window state
    - _Requirements: 1.5_

- [ ] 2. Implement frameless window with resize capability
  - [x] 2.1 Modify main window to use frameless mode


    - Set appropriate window flags for frameless mode
    - Integrate the custom title bar into the main window
    - _Requirements: 1.1_

  - [x] 2.2 Implement window resize functionality


    - Create resize handlers for window edges and corners
    - Add visual feedback for resize operations
    - Ensure minimum window size constraints
    - _Requirements: 1.6, 4.1, 4.2_

- [ ] 3. Remove menu bar and enhance toolbar
  - [x] 3.1 Remove the menu bar from the main window


    - Hide or remove the menu bar component
    - _Requirements: 2.1_

  - [x] 3.2 Add theme button to the toolbar


    - Create a theme button with appropriate icon
    - Connect the button to the theme dialog
    - _Requirements: 3.1, 3.2_

  - [x] 3.3 Ensure all functionality remains accessible


    - Add any missing functionality from menu bar to toolbar or context menus
    - Organize toolbar actions with appropriate separators
    - _Requirements: 2.2, 2.3, 2.4_

- [ ] 4. Enhance theme system integration
  - [x] 4.1 Update theme manager to style custom components


    - Ensure the title bar respects the current theme
    - Add title bar specific styles to theme definitions
    - _Requirements: 3.4, 3.6_

  - [x] 4.2 Implement theme persistence


    - Ensure selected theme is saved and restored on application restart
    - _Requirements: 3.5_

- [ ] 5. Implement responsive layout improvements
  - [x] 5.1 Enhance layout responsiveness


    - Ensure UI components adapt to window size changes
    - Implement proper scaling for small window sizes
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.2 Add high-DPI display support


    - Ensure proper scaling on high-DPI displays
    - Test with different scaling factors
    - _Requirements: 4.4_

- [ ] 6. Write tests for new components
  - [x] 6.1 Create unit tests for TitleBar component


    - Test window control button functionality
    - Test window dragging behavior
    - Test maximize/restore toggle
    - _Requirements: 1.3, 1.4, 1.5_

  - [x] 6.2 Create tests for theme integration



    - Test theme application to custom components
    - Test theme persistence
    - _Requirements: 3.4, 3.5, 3.6_