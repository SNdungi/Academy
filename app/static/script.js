function openPage(pageName,elmnt,color) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].style.backgroundColor = "";
    }
    document.getElementById(pageName).style.display = "block";
    elmnt.classList.add('active');

    document.getElementById("current_tab").value = pageName;
  }
  
  // Get the element with id="defaultOpen" and click on it
  document.getElementById("defaultOpen").click();


  var buttons = document.querySelectorAll('.tablink');

  // Add click event listener to each button
  buttons.forEach(function(button) {
    button.addEventListener('click', function() {
      // Remove 'active' class from all buttons
      buttons.forEach(function(btn) {
        btn.classList.remove('active');
      });
  
      // Add 'active' class to the clicked button
      button.classList.add('active');
    });
  });

// post info credit search 
document.getElementById('credit_customer_id').addEventListener('input', function() {
  this.value = this.value.toUpperCase();
});

document.getElementById('searchIcon').addEventListener('click', function() {
  // Perform a database search using the value of credit_customer_id
  var customerId = document.getElementById('credit_customer_id').value;

  // Make a POST request to fetch data from the server
  fetch('/creditops/view', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ customer_id: customerId }),
  })
  .then(response => response.json())
  .then(data => {
    if ('lastname' in data && 'firstname' in data && 'identity' in data && 'email' in data && 'contact' in data) {
      // Update fields with related customer info
      document.getElementById('crlastname').value = data.lastname;
      document.getElementById('crfirstname').value = data.firstname;
      document.getElementById('cridentity').value = data.identity;
      document.getElementById('cremail').value = data.email;
      document.getElementById('crcontact').value = data.contact;
  } else {
      alert('Error: Server response invalid - Please confirm ID!');
  }
})
  .catch(error => 
    alert('Error:', +error.message));
});

//guarantors calculation
function calculateTotalAmount() {
  var rows = document.querySelectorAll('tbody tr');
  var totalAmount = 0;

  rows.forEach(function(row) {
      var amountInput = row.querySelector('input[name="amount_guaranteed"]');
      if (amountInput) {
          totalAmount += parseFloat(amountInput.value) || 0;
      }
  });

  document.getElementById('total_amount').value = totalAmount.toFixed(2);
}


//guarantee tables          
function formatDecimal(input) {
  input.value = parseFloat(input.value).toFixed(2);
  }

function validateInput(input) {
  if (parseFloat(input.value) < 0) {
      input.value = "0.00";
  }
  }

  function convertToUppercase(element) {
  element.value = element.value.toUpperCase();
  }
  
  window.onload = function() {
      const textInputs = document.querySelectorAll('input[type="text"]');
      textInputs.forEach(input => {
      input.addEventListener('input', function() {
          convertToUppercase(this);
      });
      });

  };
  
  function addSubcategory(parentRow) {
          var subcategoriesTable = document.getElementById('subcategoriesTable');
          var newRow = document.createElement('tr');
          newRow.className = 'subcategory-row';
          
          var parentAmountInput = parentRow.querySelector('input[name="amount_guaranteed"]');
          var Cell = document.createElement('td');   
          var Input = document.createElement('input');
          Input.type = 'number';
          Input.name = 'amount_guaranteed';
          Input.value=parentAmountInput.value;
          Input.addEventListener('input', calculateTotalAmount);
          Input.style.color= 'brown'
          Input.style.backgroundColor= 'rgb(220, 220, 210)'
          Input.style.margin= '0';
          Input.style.height= '20px';
          Cell.appendChild(Input);
          newRow.appendChild(Cell);

          for (var i = 0; i < 3; i++) {
              var parentSubcategoryInput = parentRow.querySelector('input[name="guarantor_id' + (i + 1) + '"]');
              var Cell = document.createElement('td');
              var Input = document.createElement('input');
              Input.type = 'text';
              Input.name = 'subcategory[' + parentRow.id + ']';
              Input.addEventListener('input', convertToUppercase);
              Input.value=parentSubcategoryInput.value;
              Input.style.color= 'brown'
              Input.style.backgroundColor= 'rgb(220, 220, 210)'
              Input.style.margin= '0';
              Input.style.height= '20px';
              Input.style.textTransform= 'uppercase';
              Cell.appendChild(Input);
              newRow.appendChild(Cell);}

              var deleteCell = document.createElement('td');
              var deleteButton = document.createElement('button');
              deleteButton.textContent = 'Delete';
              deleteButton.className = 'btn-addremove';
              deleteButton.addEventListener('click', function() {
              var newRow = this.closest('tr'); // Get the closest 'tr' element
              var subcategoriesTable = newRow.parentNode; // Get the parent 'table' element
              subcategoriesTable.removeChild(newRow); // Remove the 'tr' element from the table
              calculateTotalAmount();//Recalculate the total amount after deleting a row
              });

              // deleteCell.appendChild(deleteButton);
              // newRow.appendChild(deleteCell);

          var buttonCell = parentRow.querySelector('.button-cell');
          parentRow.insertAdjacentElement('afterend', newRow);
          
      }  

//total guarantor amount
function calculateTotalAmount() {
      var elements = document.getElementsByName("amount_guaranteed");
      var totalAmount = 0;
    
        for (var i = 0; i < elements.length; i++) {
          var value = parseFloat(elements[i].value);
          if (!isNaN(value)) {
          totalAmount += value;
          }
      };
    
        document.getElementById('total_guaranteed').value = totalAmount.toFixed(2);
    }

//

function validateForm() {
    // Check if the required fields are not empty
    var requiredFields = ["reg_date", "lastname", "firstname", "othername", "email", "contact", "country_of_residence",
                          "dateofbirth", "gender", "identification", "nationality","membership_status", "confirm_details_ok"]
    for (var i = 0; i < requiredFields.length; i++) {
        var field = document.getElementById(requiredFields[i]);
        if (field.value.trim() === "") {
            alert("Please fill out all required fields.");
            return false;
        }
    }

    // Check if the checkboxes are checked
    var membershipFeePaid = document.getElementById("membership_fee");
    var confirmDetails = document.getElementById("confirm_details_ok");

    if (!membershipFeePaid.checked || !confirmDetails.checked) {
        alert("Please check both checkboxes.");
        return false;
    }

    return true;
}

//
function validateCRForm() {
  // Check if the required fields are not empty
  var requiredFields = ["credit_customer_id", "credit_amount_cr", "credit_repayment_cr", "creditProductName", "phy_address" , "res_city" , "adr_emp", "cont_emp", 
                         "crlastname","email_emp","kin_name" ,"crfirstname","kin_contact","cridentity","cremail", "crcontact" ];
  for (var i = 0; i < requiredFields.length; i++) {
      var field = document.getElementById(requiredFields[i]);
      if (field.value.trim() === "") {
          alert("Please fill out all required fields.");
          return false;
      }
  }

  // Check if the checkboxes are checked
  var confirmDetails = document.getElementById("confirm_details_ok");

  if (!membershipFeePaid.checked || !confirmDetails.checked) {
      alert("Please check both checkboxes.");
      return false;
  }

  return true;
}

// Prevent future dates
var currentDate = new Date().toISOString().split('T')[0];
document.getElementById('regdate').setAttribute('max', currentDate);
document.getElementById('reg_date').setAttribute('max', currentDate);
document.getElementById('date_ofbirth').setAttribute('max', currentDate);
document.getElementById('tx_date1').setAttribute('max', currentDate);
document.getElementById('tx_date2').setAttribute('max', currentDate);
document.getElementById('tx_date3').setAttribute('max', currentDate);

function getMembercredit() {
  // Get the value from the input field
  var memberId = document.getElementById("applied_credit_id").value;

  // Construct the URL with the member ID as a query parameter
  var url = '/member-maintenance/view?identification=' + memberId + '&tab=accountview';

  // Redirect to the URL
  window.location.href = url;
}
//Approved credit amounts
function validatecreditAmount() {
  var creditAmount = document.getElementById('credit_amount_cr').value;
  if (creditAmount < 3000 || creditAmount > 40000) {
      alert('Please enter a credit amount between 3000 and 40000.');
  }
}

function validatecreditRepayment() {
  var creditRepayment = document.getElementById('credit_repayment_cr').value;
  var repaymentValue = Number(creditRepayment);
  if (Number.isInteger(repaymentValue) && repaymentValue >= 1 && repaymentValue <= 6) {
  } else {
      alert('Please enter a whole number between 1 and 6 for the repayment period.');
  }
}

function displayAlerts() {
  var successMessage = document.getElementById('success-message').textContent;
      alert(successMessage);
}


function checkGuarantors() {
  // Add logic here to check if the form is submitted
  // For example, you can check if the 'applied_id' input is not empty
  var appliedId = document.getElementById('applied_id').value;
  
  if (appliedId.trim() === "") {
      // If the form is not submitted, prevent the link from navigating
      alert("Please submit the form first.");
      return false;
  }

  // If the form is submitted, allow the link to navigate
  return true;
}

function checkGuarantors() {
  // Add logic here to check if the form is submitted
  // For example, you can check if the 'applied_id' input is not empty
  var appliedId = document.getElementById("run_credit_auth").value;
  
  if (appliedId.trim() === "") {
      // If the form is not submitted, prevent the link from navigating
      alert("Please submit the form first.");
      return false;
  }

  // If the form is submitted, allow the link to navigate
  return true;
}


document.addEventListener("DOMContentLoaded", function() {
  // Get the value of applied_credit_id
  var appliedcreditIdValue = document.getElementById("applied_credit_id").value;


  // Set the value of current_credit_id
  document.getElementById("current_credit_id").value = appliedcreditIdValue;
});

function scrollToSection(sectionId) {
  var section = document.getElementById(sectionId);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' });
  }
}

var userConfirmed = confirm("{{ messages[0] }}");
if (!userConfirmed) {
    // User clicked cancel, prevent the form submission
    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
    });
}


document.getElementById('searchIcon').addEventListener('click', function() {
  // Perform a database search using the value of credit_customer_id
  var userId = document.getElementById('user_id').value;

  // Make a POST request to fetch data from the server
  fetch('/maintenance/change', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId }),
  })
  .then(response => response.json())
  .then(data => {
    if ('lastname' in data && 'firstname' in data && 'email' in data) {
      // Update fields with related customer info
      document.getElementById('userlastname').value = data.lastname;
      document.getElementById('userfirstname').value = data.firstname;
      document.getElementById('useremail').value = data.email;
  } else {
      alert('Error: Server response invalid - Please confirm ID!');
  }
})
  .catch(error => 
    alert('Error:', +error.message));
});

function displaySelectedItem() {
  var selectElement = document.getElementById('itemList');
  var selectedItemsContainer = document.getElementById('selectedItemsContainer');

  // Create a new div element for the selected item
  var newItemDiv = document.createElement('div');
  newItemDiv.textContent = selectElement.options[selectElement.selectedIndex].text;

  // Append the new item div to the container
  selectedItemsContainer.appendChild(newItemDiv);
}

document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.querySelector('#sidebarMenu');
  const mainContent = document.querySelector('.col-md-10');
  
  sidebar.addEventListener('hidden.bs.collapse', function () {
    mainContent.classList.remove('col-md-11');
    mainContent.classList.add('col-md-12');
  });
  
  sidebar.addEventListener('shown.bs.collapse', function () {
    mainContent.classList.remove('col-md-12');
    mainContent.classList.add('col-md-11');
  });
});

function updateCircles() {
  const circleCount = document.getElementById('circleCount').value;
  const circles = document.querySelectorAll('.circle');
  circles.forEach((circle, index) => {
    if (index < circleCount) {
      circle.style.backgroundColor = 'blue'; // Change color to make circles visible
    } else {
      circle.style.backgroundColor = 'transparent'; // Make circles invisible
    }
  });
}

// Listen for input change event
document.getElementById('circleCount').addEventListener('input', updateCircles);

// Initial update
updateCircles();

function validateInputs(input) {
  let value = input.value;
  let validChars = /[0-9+\-*/]/g; // Regular expression for valid characters
  let newValue = value.replace(validChars, ''); // Remove any invalid characters
  input.value = newValue; // Update the input value
}