# MongoDB: First impressions

MongoDB is a fairly simple database to begin using, but I would
like there to be a bit more straightforward documentation for
those of us who would like to move beyond the simple use of it
and try something less trivial.

There are a bunch of tutorials on the site, but most all of them
deal with installation or more advanced administration issues, like
database sharding.
Although these are certainly important topics, there seems to be
no help for the intermediate developer trying to figure out how a
good MongoDB database should really be designed.

(*A little nitpick; I wish the introduction docs were not centered*
 *around getting an account on the MongoDB Atlas cloud service.*)

## Installation

So installation on Linux and MacOSX seems pretty straightforward.
As usual, the installation docs don't really have any kind of
checklist for testing that you have a successful installation.
It would have been nice to not have to query a half dozen
stackoverflow questions just to find out what the MongoDB
server daemon is called, and where it reads its default
configuration.  On Linux, I found it here, but only after I
restarted the system post-install:

```
$ ps -ef |grep -i mongo |grep -v grep
mongodb    838     1  0 Feb24 ?        00:40:26 /usr/bin/mongod --unixSocketPrefix=/run/mongodb --config /etc/mongodb.conf

```

Ok, so it's installed.  How do I use it?  Well, the getting started
guide tells us that for Python, we need to use PyMongo package.
So we install it.  Installation of this package is not too eventful
or interesting.  But once it is done, you should be able to do the
following:

```
$ ipython

In [1]: import pymongo
In [2]: from pymongo import MongoClient
In [3]: client = MongoClient()
In [4]: db = client.test_database
In [5]: collection = db.test_collection
In [6]:
```

Ok, so pretty easy.  Basically if you can do this, your installation
is probably healthy for development at least.


## Database Storage

I won't reiterate any of the details of creating/deleting documents
here, but will refer to 
[the PyMongo tutorial](https://api.mongodb.com/python/current/tutorial.html#documents).

Basically MongoDB documents are stored as BSON, which they say is a
binary serialization format.  And in order to represent BSON, an
[extended version of JSON](https://docs.mongodb.com/manual/reference/mongodb-extended-json/index.html)
is used by clients communicating with MongoDB.
In Python, this looks like a structure of lists, dicts, and data
represented by mostly built-in data types, 

It seems that documents in a collection are not restricted in the
data structures that can be used.  And they can change from
document to document.

## Database Querying

Querying documents in MongoDB is also done using JSON styled
structures.  That is, you would pass in a JSON structure of dicts,
lists, and data that conform to MongoDB's
[query operators](https://docs.mongodb.com/manual/reference/operator/)
format.

It seems actually pretty nice for querying.  I think the fact that
it is formed through JSON will lend a bit of robustness that SQL
statements never had.

In SQL, it possible to form literal commands to modify the
database, and send them directly in string form.  This technique is
generally called "Embedded SQL", and without any validation, led to
the infamous SQL injection attacks that affected a lot of websites
about ten years ago.

Abuse of JSON structures is not unheard of, I'm sure.  And a web
server based on a Javascript runtime (Node.js) may need to be
careful accepting such a request without some kind of validation.
But a Python based web server (Pyramid or Django) receiving such a
request would parse the payload into Python defined structures in
order to use it, and it is unlikely that any Javascript
vulnerabilities would make it through to the Python runtime.

(*There is of course the jsonpickle module, which serializes python*
 *objects into JSON and back, and it is dangerous to use this for*
 *communicating across the web.  But it is easy to simply not use*
 *that package.*)

I am not going to proclaim that it's completely bulletproof, but
it seems that only a very sophisticated attack would work in this
scenario, because the attack itself would need to be representable
in JSON and parseable into something Python understands as a
command or statement.

## Document Data Structures

The level of data structure flexibility that MongoDB affords you
is a very welcome feature.  It is nice to be able to handle
different types of documents or update document structures without
needing to manage the underlying database structure definitions.

With SQL, one needed to plan any changes in the table schemas.
Table columns could be added, but for a large populated table,
space would need to be allocated for every existing row, and some
reasonable migration plan would need to be made for loading
reasonable values into the field.

I've worked with earlier incarnations of object databases before.
And though they did not use data tables, they did maintain object
class definitions.  So these object databases did not save you from
any of the complexity involved in changing class definitions.  

MongoDB appears to have a great deal of flexibility in that area.
There doesn't appear to be any penalty, at least internal to the
database, in updating document data structures, or even supporting
multiple document types in the same collection.

Of course any client programs that use the database will need to be
updated to handle changes in the data structures, and this is true
in all cases, whether its a relational or object database.  It may
be too early to weigh in on this, but it does seem to me that with
the database maintaining a rigid schema, client programs would only
need smaller incremental updates, and could depend on a reasonably
consistent data structure for all data records that they managed,
and thus a consistent level of complexity.

With MongoDB it is not unreasonable to think that a client program
may need to be able to handle not just updates to data structures,
but bigger and more frequent changes.  It may very well need to
maintain compatibility with a long list of older document formats,
as well as completely different document types.

[next: MongoDB Documents](mongodb_documents.md)
