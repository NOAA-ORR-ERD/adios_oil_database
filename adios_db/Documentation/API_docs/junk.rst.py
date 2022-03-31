Navigate a period ('.') delimited path of attribute values into the
oil data structure and set a value at that location in the
structure.

Example paths:

- sub_samples.0.metadata.sample_id  (sub_samples is assumed to be
     a list, and we go to the zero index for that part)

- physical_properties.densities.-1  (densities is assumed to be a
  list, goes to the last item)

- physical_properties.densities.+   (appends an item to the
  densities list and goes to that part.  the index value
  is assumed to be -1 in this case)
