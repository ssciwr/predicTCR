describe("Home page", () => {
  it("visits the app root url", () => {
    cy.intercept(
      {
        method: "GET",
        url: "/api/remaining",
      },
      { remaining: 67 },
    );
    cy.visit("/");
    cy.contains("Remaining available samples this week: 67");
  });
});
