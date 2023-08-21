Add-Type -AssemblyName System.Windows.Forms

# Create the main form
$form = New-Object Windows.Forms.Form
$form.Text = "PowerShell GUI"
$form.Size = New-Object Drawing.Size(400, 300)

# Create a label
$label = New-Object Windows.Forms.Label
$label.Text = "Hello, PowerShell GUI!"
$label.Location = New-Object Drawing.Point(100, 50)
$form.Controls.Add($label)

# Create a button
$button = New-Object Windows.Forms.Button
$button.Text = "Click Me"
$button.Location = New-Object Drawing.Point(150, 100)
$button.Add_Click({
    $label.Text = "Button Clicked!"
})
$form.Controls.Add($button)

# Show the form
$form.ShowDialog()