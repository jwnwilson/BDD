Feature: Noel wilson home page.

  Scenario: User navigates to home page and observes page content
    When I go to the home page
    Then On home page I want to see Welcome
  
  Scenario: User navigates portfolio
    When I go to the home page
    And I click on "Portfolio" on the home page
    Then I see "Portfolio" on the home page
