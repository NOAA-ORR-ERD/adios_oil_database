# Considerations for MongoDB Documents

As we noted earlier, a MongoDB database contains collections of documents that
are stored in BSON format, and externally managed in MongoDB extended JSON.
And any organization of document data should work as long as it conforms to
JSON.
This gives a lot of flexibility in the types of documents that are possible,
But I think it makes the job more difficult for any system that interacts
with the database.

## MongoDB Extended JSON

JSON is fairly easy to work with in Python, but it would be nice to not have
to use subscript notation when accessing every single data item in a document.
Consider the following snippet:

```
    json_data['densities'][0]['ref_temp_k']
```
in contrast to...
```
    json_obj.densities[0].ref_temp_k
```

Syntactically, a raw JSON structure is less readable than the equivalent
Python record object's dot notation.  At least I think so.
A minor detail perhaps?  Trivial even?  Maybe, but consider this effect over
an entire body of source code.

So I would like to be able to use object attributes instead of list and
dictionary subscripts.

## A Veritable Cornucopia of Documents

With rigid schemas defining the data structures and object types to be used,
A client program would certainly need to validate that a particular data item
contained a good, or at least sane, value.  But the data item was nearly
guaranteed to be there.

But without any schemas to speak of, a document may not even have the data
element to begin with.  In fact, there may be entire sections missing from
a document that a client program may be expecting.

Here's a little taste in Python:

```
if len(json_obj.dvis) > 0 and json_obj.dvis[0].ref_temp_k is None:
    raise SomeException
```
This is a naive check to see if a data item has a useable value.  Here we
perform two checks:
- the list attribute 'dvis' is not empty, and...
- the attribute 'ref_temp_k' of the first list item is None

Now we have made some assumptions about the object we are working with.
First we assume that our object has a 'dvis' attribute, and second, we assume
that the first list item has a 'ref_temp_k' attribute.  The reason that one
might be able to do this with a high level of certainty is if the data
structure of our objects is defined and validated by a SQLAlchemy (*or
something similar*) model class, or maybe it is in fact a Python class object
that is known to have those member attributes.

If we couldn't be certain about a documents structure, then we would need to
put in additional checks:

```
if (hasattr(json_obj, 'dvis') and
        len(json_obj.dvis) > 0 and
        hasattr(json_obj.dvis[0], 'ref_temp_k') and
        json_obj.dvis[0].ref_temp_k is None):
    raise SomeException
```

At face value, this is about twice the complexity of the original check, and it
may even raise new questions like "Does this mean I also need to check
*some_other_place*?", which could increase the code's complexity even further.
Complexity increases like this, due to the uncertainty of the underlying data
structure, can really add up across a project.

It would be really nice to reduce, or at least contain, the potential
complexity that an open-ended document structure introduces.  In short, I would
like to have Model class definitions to validate incoming records, control how
they are stored and retrieved, and give some certainty that, even if we are
managing multiple document structures, there will be a known *set* of documents
that a client can identify.  We might not want to use Model objects exclusively
everywhere, but I certainly don't want to **not** have them.

## PyMODM: Model Objects for MongoDB

As it would turn out, There are a
[number of projects](http://api.mongodb.com/python/current/tools.html#orm-like-layers)
, separate from MongoDB,
that implement some kind of model architecture on top of it.  I investigated
a number of them initially, running into a couple of dead ends on some.  I
ended up choosing PyMODM because it is maintained by engineers at MongoDB.  This
fact gives me confidence that the project will likely be maintained for as long
as MongoDB is maintained.

[PyMODM Model classes](http://pymodm.readthedocs.io/en/stable/api/index.html#module-pymodm.fields)
look quite similar to those of SQLAlchemy in their syntax, in fact maybe a bit
simpler, but so far I have found them to be equally expressive.  In fact while
implementing a unique constraint on a group of fields, I noticed a
[particular difference](https://sqlite.org/faq.html#q26)
in how a number of SQL products implement unique constraints in which I feel
MongoDB (via PyMODM) has the better behavior.

As mentioned earlier we may not want to use model class objects everywhere,
and there is no reason I can see where you would need to.  I don't see anything
about PyMODM that locks you in or forces you to use them once you have made the
decision to use this package.  So where would we want to use them, and where
would we like to just use the base MongoDB functionality?

### Importing New Documents

The introduction of new records I think is one obvious place where we would
need to validate the data and control how that data looks.  After all, once the
data is in our system, it will persist.  And if the data is wrong, it will
persist wrongly.  Once in the system it can take quite awhile before someone
notices that a record has incorrect data.

Incorrect data can take a lot of different forms, and we probably can't detect
them all, but we can do a lot to mitigate the most egregious instances.
We can at a minimum detect:
- Whether a record should be unique in the system
- If a record has a minimum set of required information
- If groups of data points have a minimum set of required information (e.g. if
  there exists a distillation cut within an oil record, does it have a fraction
  and an associated temperature?)

Implementing Model classes for records to be introduced into the database will
add a level of certainty in the documents that are being created, and will make
it easier for all other sytems that might interact with the database.

### Document Forms

This is an area that might go either way in regards to needing the use of model
classes.  I have a hunch it would depend upon the amount of detail that is
needed by the form.  I believe that the majority of forms could make use of a
model class designed to ease the retrieval of data points inside a document.

A form designed primarily to display most or all document content, like an edit
form, would of course be best implemented using a document model class.
But a form that would display only one or a few data points, such as a popup
notification form, may not need it.

### Querying Documents

Without going into any specifics, a query of the database consists primarily
of using the incoming JSON query parameters to query the database, getting the
JSON data results, and sending it back.  So this probably does not require the
use of document model classes.




