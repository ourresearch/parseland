# Parseland

This API parses and returns author and affiliation data from landing pages.

### Example

`/parse?doi=10.1016/j.actaastro.2021.05.018`

Output:

```yaml
{
  "message": [
    {
      "name": "Maksim Shirobokov",
      "affiliations": [
        "Moscow Center for Fundamental and Applied Mathematics, 4 Miusskaya Pl., Moscow 125047, Russia"
      ]
    },
    {
      "name": "Sergey Trofimov",
      "affiliations": [
        "Moscow Center for Fundamental and Applied Mathematics, 4 Miusskaya Pl., Moscow 125047, Russia"
      ]
    },
    {
      "name": "Mikhail Ovchinnikov",
      "affiliations": [
        "Moscow Center for Fundamental and Applied Mathematics, 4 Miusskaya Pl., Moscow 125047, Russia"
      ]
    }
  ],
  "metadata": {
    "parser": "sciencedirect",
    "doi": "10.1016/j.actaastro.2021.05.018",
    "doi_url": "https://doi.org/10.1016/j.actaastro.2021.05.018"
  }
}