// This is the script for our app

console.log("I'm ALIVE!");

const logout = () => {
  // We will request a logout from the backend
  fetch("/logout")
    .then((response) => {
      console.log("Logged out, response: ", response);
      location.reload();
    })
    .catch((reason) => {
      console.log("ERROR while logging out: ", reason);
    });
};
