import os
import re as RegEx


#=============================================================
# Load a file, look for tables, if any are found, change them to SimpleTable format and return the result
def ProcessFile(filename):
    if not os.path.exists(filename):
        #log.Write()
        return

    # Read the file
    with open(filename) as file:
        source=file.read()

    # The file can be viewed as spans of <stuff> interspersed with "{{"<other stuff>"}}"
    # So analyze the file into a list of those components
    # We will assume that the "{{" and "}} are always balanced!
    chunks=[]
    while len(source) > 0:
        if source[0:2] == "{{":
            # Next chunk is a "{{xx}}"
            loc=source.find("}}")
            if loc < 0:
                print("**something's wrong!")
                break
            chunks.append(source[0:loc+2])
            source=source[loc+2:]
        else:
            # Next chunk is not a "{{xx}}"
            loc=source.find("{{")
            if loc < 0:
                loc=len(source) # Then all that's left is part of the chunk
            chunks.append(source[0:loc])
            source=source[loc:]

    # Now I search the chunks for two chunks in a row that begin "{{Sequence..."  and then one that begins "{{convention" (with nothing more than whitespace between them).
    # Now we search the chunks for one or more s's and one c in any order. The first s is merged with the c and any other s is ignored.
    chunkTypes=""
    for chunk in chunks:
        if chunk.startswith("{{Sequence"):
            chunkTypes=chunkTypes+"s"
        elif chunk.startswith("{{convention"):
            chunkTypes=chunkTypes+"c"
        elif len(chunk) == 0 or chunk.isspace():
            chunkTypes=chunkTypes+"w"
        else:
            chunkTypes=chunkTypes+"x"

    # Now we have a text string which shows the pattern of chunks.
    # We're looking for a sequence with an s and a c  with any number of "w"s interspersed, but no "x"s.
    # Use Regex.
    indexFirstSeq=None
    indexConv=None

    pattern1="(s)[sw]*(c)"  # We care about the 1st S and the only C
    pattern2="(c)w*(s)"     # Because we only care about the 1st S, we don't need to look for any others
    m=RegEx.search(pattern1, chunkTypes)    # Check pattern 1
    if m is not None:
        # OK, we've found one.
        x=m.span()
        # There are two {{Sequences.  The first one needs to be analyzed and removed and merged into the {{convention
        indexFirstSeq=x[0]
        indexConv=x[1]-1
    else:
        m=RegEx.search(pattern2, chunkTypes)    # And check for pattern 2
        if m is not None:
            # OK, we've found one.
            x=m.span()
            # We found a {{Sequence after the {{convention and  in needs to be analyzed and removed and merged into the {{convention
            indexConv=x[0]
            indexFirstSeq=x[1]-1

    conv=None
    if indexFirstSeq is not None:
        firstSeq=chunks[indexFirstSeq]
        conv=chunks[indexConv]

        # Now pattern match the structure of the {{Sequence string to pull out the two convention names
        pattern="before=\[\[(.*)\]\]\s*\|\s*after=\[\[(.*)\]\]"   # Match: before=[[xxx]] | after=[[yyy]]
        m=RegEx.search(pattern, firstSeq)
        if m is not None:
            conv1=m.groups()[0]
            conv2=m.groups()[1]

            # Now merge the names into the {{convention line, right before the closeing "}}"
            conv=conv[:-2]+" | before=[["+conv1+"]] | after=[["+conv2+"]]}}"

        # Process the chunks deleting one and replacing another
        chunks[indexConv]=conv
        del chunks[indexFirstSeq]

    return chunks



newSite=""
oldSite=r"C:\Users\mlo\Dropbox\mlo"
page="baycon.mediawiki"
page="magicon.mediawiki"
page="westercon-71.mediawiki"
page="2kon1.mediawiki"
page="2kon2.mediawiki"
page="satellite-4.mediawiki"

newfile=ProcessFile(os.path.join(oldSite, page))
with open(os.path.join(newSite, page), "w") as file:
    newfile=[n+"\n" for n in newfile]
    file.writelines(newfile)